from ultralytics import YOLO

model = YOLO("yolov8m.pt")

train = model.train(data="data.yaml", epochs=30)
val = model.val()
results = model.predict("pano.jpg")
result = results[0]

print(len(result.boxes))
box = result.boxes[0]
for box in result.boxes:
  class_id = result.names[box.cls[0].item()]
  cords = box.xyxy[0].tolist()
  cords = [round(x) for x in cords]
  conf = round(box.conf[0].item(), 2)
  print("Object type:", class_id)
  print("Coordinates:", cords)
  print("Probability:", conf)
  print("---")
succ = model.export()
# result = model.predict("pano.jpg")
# print(result)
