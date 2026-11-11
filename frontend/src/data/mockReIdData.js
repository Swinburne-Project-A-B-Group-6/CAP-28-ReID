export const identities = [
  {
    globalId: 1,
    history: [
      { cameraId: 'CAM-01', start: 0, end: 24.08 },
      { cameraId: 'CAM-02', start: 0, end: 18.68 },
      { cameraId: 'CAM-03', start: 0, end: 3.92 },
      { cameraId: 'CAM-03', start: 4.76, end: 18.2 }
    ]
  },
  {
    globalId: 2,
    history: [
      { cameraId: 'CAM-02', start: 0, end: 22.76 },
      { cameraId: 'CAM-03', start: 0, end: 3.2 },
      { cameraId: 'CAM-03', start: 3.8, end: 8.84 },
      { cameraId: 'CAM-01', start: 14.96, end: 25 },
      { cameraId: 'CAM-03', start: 22.88, end: 25 },
      { cameraId: 'CAM-02', start: 23.36, end: 25 }
    ]
  },
  {
    globalId: 3,
    history: [
      { cameraId: 'CAM-02', start: 14.84, end: 25 },
      { cameraId: 'CAM-03', start: 16.4, end: 25 },
      { cameraId: 'CAM-01', start: 19.88, end: 25 }
    ]
  }
]

export const eventLogs = [
  { id: '0:1', globalId: 1, cameraId: 'CAM-01', status: 'New Person', time: 0 },
  { id: '2:1', globalId: 1, cameraId: 'CAM-02', status: 'Re-identified', time: 0.4 },
  { id: '4:1', globalId: 1, cameraId: 'CAM-03', status: 'Re-identified', time: 0.8 },
  { id: '0:2', globalId: 2, cameraId: 'CAM-02', status: 'New Person', time: 1.2 },
  { id: '2:2', globalId: 2, cameraId: 'CAM-03', status: 'Re-identified', time: 1.6 },
  { id: '3:2', globalId: 2, cameraId: 'CAM-03', status: 'Exited', time: 3.2 },
  { id: '5:1', globalId: 1, cameraId: 'CAM-03', status: 'Exited', time: 3.92 },
  { id: '4:2', globalId: 2, cameraId: 'CAM-03', status: 'Exited', time: 8.84 },
  { id: '0:3', globalId: 3, cameraId: 'CAM-02', status: 'New Person', time: 14.84 },
  { id: '5:2', globalId: 2, cameraId: 'CAM-01', status: 'Re-identified', time: 14.96 },
  { id: '1:3', globalId: 3, cameraId: 'CAM-03', status: 'Re-identified', time: 16.4 },
  { id: '6:1', globalId: 1, cameraId: 'CAM-03', status: 'Exited', time: 18.2 },
  { id: '3:1', globalId: 1, cameraId: 'CAM-02', status: 'Exited', time: 18.68 },
  { id: '2:3', globalId: 3, cameraId: 'CAM-01', status: 'Re-identified', time: 19.88 },
  { id: '1:2', globalId: 2, cameraId: 'CAM-02', status: 'Exited', time: 22.76 },
  { id: '1:1', globalId: 1, cameraId: 'CAM-01', status: 'Exited', time: 24.08 }
]
