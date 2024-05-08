from gpiozero import DistanceSensor

us_sensor = DistanceSensor(echo=0, trigger=1, threshold_distance=0.1, max_distance=2)

def in_range():
    print(f'In range {us_sensor.distance}')

def out_of_range():
    print(f'Out of range {us_sensor.distance}')

us_sensor.when_in_range = in_range
us_sensor.when_out_of_range = out_of_range

# print(dir(us_sensor))

while True:
    # print(f'Distance: {us_sensor.distance}')
    us_sensor.wait_for_in_range()
    # print(f'In range {us_sensor.distance}')
    us_sensor.wait_for_out_of_range()
    # print(f'Out of range {us_sensor.distance}')
