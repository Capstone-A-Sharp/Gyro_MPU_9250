import serial
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 시리얼 포트 설정 (변경 필요)
ser = serial.Serial('/dev/cu.usbserial-A5069RR4', 115200)

# 그래프 설정
plt.ion()
fig = plt.figure(figsize=(12, 6))

# 3D 시각화
ax3d = fig.add_subplot(121, projection='3d')

# 2D RPY 그래프
ax2d = fig.add_subplot(122)
ax2d.set_title("Roll, Pitch, Yaw (Real-Time)")
ax2d.set_xlabel("Time (frames)")
ax2d.set_ylabel("Angle (°)")
ax2d.set_ylim([-180, 180])
r_line, = ax2d.plot([], [], label="Roll", color='r')
p_line, = ax2d.plot([], [], label="Pitch", color='g')
y_line, = ax2d.plot([], [], label="Yaw", color='b')
ax2d.legend(loc="upper right")

# RPY 저장 버퍼
BUFFER_SIZE = 100
roll_buffer, pitch_buffer, yaw_buffer = [], [], []

def rotation_matrix(roll, pitch, yaw):
    r = np.deg2rad(roll)
    p = np.deg2rad(pitch)
    y = np.deg2rad(yaw)

    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(r), -np.sin(r)],
        [0, np.sin(r), np.cos(r)]
    ])
    Ry = np.array([
        [np.cos(p), 0, np.sin(p)],
        [0, 1, 0],
        [-np.sin(p), 0, np.cos(p)]
    ])
    Rz = np.array([
        [np.cos(y), -np.sin(y), 0],
        [np.sin(y), np.cos(y), 0],
        [0, 0, 1]
    ])
    return Rz @ Ry @ Rx

def draw_3d_orientation(R):
    ax3d.clear()
    ax3d.set_xlim([-1, 1])
    ax3d.set_ylim([-1, 1])
    ax3d.set_zlim([-1, 1])
    ax3d.set_title("MPU9250 Orientation")
    ax3d.set_xlabel("X (Roll)")
    ax3d.set_ylabel("Y (Pitch)")
    ax3d.set_zlabel("Z (Yaw)")

    origin = np.array([0, 0, 0])
    axis_len = 0.8
    x_axis = R @ np.array([axis_len, 0, 0])
    y_axis = R @ np.array([0, axis_len, 0])
    z_axis = R @ np.array([0, 0, axis_len])

    ax3d.quiver(*origin, *x_axis, color='r', label='X-axis (Roll)')
    ax3d.quiver(*origin, *y_axis, color='g', label='Y-axis (Pitch)')
    ax3d.quiver(*origin, *z_axis, color='b', label='Z-axis (Yaw)')
    ax3d.legend()

def update_2d_plot():
    x = list(range(len(roll_buffer)))
    r_line.set_data(x, roll_buffer)
    p_line.set_data(x, pitch_buffer)
    y_line.set_data(x, yaw_buffer)
    ax2d.set_xlim(0, BUFFER_SIZE)

while True:
    try:
        line = ser.readline().decode(errors='ignore').strip()
        if line == "END":
            continue

        data = json.loads(line)
        mpu = data.get("MPU9250", {})

        # 센서 데이터 수집
        ax_val = mpu["accel"]["x"]
        ay_val = mpu["accel"]["y"]
        az_val = mpu["accel"]["z"]

        gx_val = mpu["gyro"]["x"]
        gy_val = mpu["gyro"]["y"]
        gz_val = mpu["gyro"]["z"]

        mx_val = mpu["mag"]["x"]
        my_val = mpu["mag"]["y"]
        mz_val = mpu["mag"]["z"]

        roll = mpu["roll"]
        pitch = mpu["pitch"]
        yaw = mpu["yaw"]

        # 콘솔 출력
        print("========== MPU9250 ==========")
        print(f"Accel : x={ax_val:.3f}, y={ay_val:.3f}, z={az_val:.3f}")
        print(f"Gyro  : x={gx_val:.3f}, y={gy_val:.3f}, z={gz_val:.3f}")
        print(f"Mag   : x={mx_val:.3f}, y={my_val:.3f}, z={mz_val:.3f}")
        print(f"RPY   : Roll={roll:.2f}°, Pitch={pitch:.2f}°, Yaw={yaw:.2f}°")
        print("================================\n")

        # 버퍼 업데이트
        roll_buffer.append(roll)
        pitch_buffer.append(pitch)
        yaw_buffer.append(yaw)

        if len(roll_buffer) > BUFFER_SIZE:
            roll_buffer.pop(0)
            pitch_buffer.pop(0)
            yaw_buffer.pop(0)

        # 시각화 업데이트
        R = rotation_matrix(roll, pitch, yaw)
        draw_3d_orientation(R)
        update_2d_plot()
        plt.pause(0.05)

    except json.JSONDecodeError:
        print("⚠️ JSON 파싱 실패")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")