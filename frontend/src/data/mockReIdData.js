export const identities = [
  {
    globalId: 1,
    attributes: ['Long Sleeves', 'Light Pants'],
    history: [
      { cameraId: 'CAM-01', localId: 2, enterTime: '00:00', exitTime: '00:23' },
      { cameraId: 'CAM-02', localId: 16, enterTime: '00:08' },
      { cameraId: 'CAM-03', localId: 10, enterTime: '00:12' }
    ]
  },
  {
    globalId: 2,
    attributes: ['Long Sleeves', 'Light Pants'],
    history: [
      { cameraId: 'CAM-02', localId: 2, enterTime: '00:01' },
      { cameraId: 'CAM-03', localId: 9, enterTime: '00:06' },
      { cameraId: 'CAM-01', localId: 16, enterTime: '00:15' }
    ]
  },
  {
    globalId: 3,
    attributes: ['Long Sleeves', 'Dark Pants'],
    history: [
      { cameraId: 'CAM-02', localId: 22, enterTime: '00:09' },
      { cameraId: 'CAM-03', localId: 24, enterTime: '00:14' },
      { cameraId: 'CAM-01', localId: 25, enterTime: '00:18' }
    ]
  }
]

export const eventLogs = [
  { id: 'EVT-10', timestamp: '00:23', camera: 'CAM-01', localId: 2, globalId: 1, eventType: 'EXITED' },
  { id: 'EVT-09', timestamp: '00:18', camera: 'CAM-01', localId: 25, globalId: 3, eventType: 'RE_IDENTIFIED', confidence: 86 },
  { id: 'EVT-08', timestamp: '00:15', camera: 'CAM-01', localId: 16, globalId: 2, eventType: 'RE_IDENTIFIED', confidence: 88 },
  { id: 'EVT-07', timestamp: '00:14', camera: 'CAM-03', localId: 24, globalId: 3, eventType: 'RE_IDENTIFIED', confidence: 82 },
  { id: 'EVT-06', timestamp: '00:12', camera: 'CAM-03', localId: 10, globalId: 1, eventType: 'RE_IDENTIFIED', confidence: 91 },
  { id: 'EVT-05', timestamp: '00:10', camera: 'CAM-03', localId: 15, globalId: null, eventType: 'LOW_CONFIDENCE', confidence: 64, attributes: ['Unknown'] },
  { id: 'EVT-04', timestamp: '00:09', camera: 'CAM-02', localId: 22, globalId: 3, eventType: 'NEW_PERSON' },
  { id: 'EVT-03', timestamp: '00:08', camera: 'CAM-02', localId: 16, globalId: 1, eventType: 'RE_IDENTIFIED', confidence: 89 },
  { id: 'EVT-02', timestamp: '00:06', camera: 'CAM-03', localId: 9, globalId: 2, eventType: 'RE_IDENTIFIED', confidence: 84 },
  { id: 'EVT-01', timestamp: '00:01', camera: 'CAM-02', localId: 2, globalId: 2, eventType: 'NEW_PERSON' },
  { id: 'EVT-00', timestamp: '00:00', camera: 'CAM-01', localId: 2, globalId: 1, eventType: 'NEW_PERSON' }
]
