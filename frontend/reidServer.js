import { execFile } from 'node:child_process'
import { createReadStream, existsSync } from 'node:fs'
import { mkdir, mkdtemp, open, readFile, rename, rm, stat, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pipeline } from 'node:stream/promises'
import { fileURLToPath } from 'node:url'
import { promisify } from 'node:util'

const run = promisify(execFile)
const project = fileURLToPath(new URL('../', import.meta.url))
const ai = join(project, 'AI')
const publicDir = join(project, 'frontend', 'public')
const api = '/api/reid'

function reply(response, status, data) {
  if (response.destroyed) return
  response.writeHead(status, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' })
  response.end(JSON.stringify(data))
}

function uploadMetadata(request) {
  if (request.headers['content-type'] !== 'application/octet-stream') return null
  try {
    const videos = JSON.parse(request.headers['x-reid-videos'])
    if (!Array.isArray(videos) || videos.length < 2 || !videos.every((video) =>
      Number.isSafeInteger(video?.size) && video.size > 0 &&
      typeof video.extension === 'string' && /^[a-z0-9]{1,5}$/.test(video.extension)
    )) return null
    if (videos.reduce((total, video) => total + video.size, 0) !== Number(request.headers['content-length'])) {
      return null
    }
    return videos
  } catch {
    return null
  }
}

async function receiveVideos(request, folder, videos) {
  const paths = videos.map(({ extension }, index) => join(folder, `input-${index}.${extension}`))
  let index = 0
  let remaining = videos[0].size
  let file
  try {
    for await (const chunk of request) {
      let offset = 0
      while (offset < chunk.length) {
        if (index === videos.length) throw new Error('The video upload exceeded its declared size.')
        file ??= await open(paths[index], 'wx')
        const length = Math.min(chunk.length - offset, remaining)
        await file.writeFile(chunk.subarray(offset, offset + length))
        offset += length
        remaining -= length
        if (remaining === 0) {
          await file.close()
          file = undefined
          remaining = videos[++index]?.size
        }
      }
    }
    if (index !== videos.length) throw new Error('The video upload ended early.')
    return paths
  } finally {
    await file?.close()
  }
}

async function processVideos(folder, inputs) {
  const venv = join(ai, '.venv', ...(process.platform === 'win32' ? ['Scripts', 'python.exe'] : ['bin', 'python']))
  const python = process.env.REID_PYTHON || (existsSync(venv) ? venv : 'python')
  const output = join(folder, 'videos')
  const tracking = join(folder, 'tracking.json')
  const cameras = inputs.flatMap((input, index) => ['--camera', `CAM-${String(index + 1).padStart(2, '0')}=${input}`])
  try {
    await run(python, [join(ai, 'run_reid.py'), ...cameras, '--output', output, '--tracking', tracking],
      { cwd: project, windowsHide: true })
  } catch (error) {
    if (error.code === 'ENOENT') throw new Error('Python was not found. Set up the AI environment in README.md.')
    const reason = error.stderr?.trim().split(/\r?\n/).at(-1)
    throw new Error(reason || 'The Re-ID process failed.')
  }

  const json = await readFile(tracking, 'utf8')
  const data = JSON.parse(json)
  await Promise.all(inputs.map((input) => rm(input)))
  const id = folder.split(/[\\/]/).at(-1)
  await mkdir(publicDir, { recursive: true })
  const pending = join(publicDir, `.${id}.tmp`)
  try {
    await writeFile(pending, json, { flag: 'wx' })
    await rename(pending, join(publicDir, 'tracking.json'))
  } finally {
    await rm(pending, { force: true })
  }
  return {
    ...data,
    cameras: data.cameras.map((camera) => ({ ...camera, src: `${api}/videos/${id}/${camera.file}` }))
  }
}

async function sendVideo(request, response, file) {
  const { size } = await stat(file)
  const headers = { 'Accept-Ranges': 'bytes', 'Content-Type': 'video/mp4' }
  let start = 0
  let end = size - 1
  if (request.headers.range) {
    const [, first, last] = /^bytes=(\d*)-(\d*)$/.exec(request.headers.range) ?? []
    if (first === '' && last) start = Math.max(0, size - Number(last))
    else if (first) {
      start = Number(first)
      if (last) end = Math.min(end, Number(last))
    } else {
      start = size
    }
    if (start > end) {
      response.writeHead(416, { 'Content-Range': `bytes */${size}` }).end()
      return
    }
    headers['Content-Range'] = `bytes ${start}-${end}/${size}`
  }
  headers['Content-Length'] = end - start + 1
  response.writeHead(request.headers.range ? 206 : 200, headers)
  await pipeline(createReadStream(file, { start, end }), response)
}

export function reidServer() {
  let busy = false
  let current
  const cleanup = (folder) => rm(folder, { recursive: true, force: true }).catch(console.warn)

  async function handle(request, response, next) {
    const path = request.url.split('?')[0]
    if (!path.startsWith(`${api}/`) && path !== api) return next()

    if (request.method === 'GET' && current) {
      const camera = current.session.cameras.find(({ src }) => src === path)
      if (camera) {
        try {
          await sendVideo(request, response, join(current.folder, 'videos', camera.file))
        } catch {
          if (!response.headersSent) reply(response, 404, { error: 'Video unavailable.' })
        }
        return
      }
    }
    if (request.method !== 'POST' || path !== api) {
      return reply(response, 404, { error: 'Re-ID endpoint not found.' })
    }

    const origin = request.headers.origin
    const protocol = request.socket.encrypted ? 'https' : 'http'
    if (origin && origin !== `${protocol}://${request.headers.host}`) {
      return reply(response, 403, { error: 'Open the dashboard from the local Re-ID server.' })
    }
    if (busy) return reply(response, 409, { error: 'Another folder is being processed.' })
    const videos = uploadMetadata(request)
    if (!videos) return reply(response, 400, { error: 'Choose a folder with at least two video files.' })

    busy = true
    let folder
    try {
      folder = await mkdtemp(join(tmpdir(), 'cap28-session-'))
      const inputs = await receiveVideos(request, folder, videos)
      const session = await processVideos(folder, inputs)
      const previous = current
      current = { folder, session }
      if (previous) await cleanup(previous.folder)
      reply(response, 200, session)
    } catch (error) {
      if (folder) await cleanup(folder)
      reply(response, 422, { error: error.message })
    } finally {
      busy = false
    }
  }

  function register(server) {
    server.middlewares.use(handle)
    server.httpServer?.once('close', () => {
      if (current) void cleanup(current.folder)
    })
  }
  return { name: 'cap28-reid', configureServer: register, configurePreviewServer: register }
}
