import serial
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 시리얼 포트 설정
ser = serial.Serial('/dev/cu.usbserial-A5069RR4', 115200)

# Matplotlib 설정
plt.ion()
fig = plt.figure(figsize=(12, 6))

# 왼쪽: 3D 회전 상태
ax3d = fig.add_subplot(121, projection='3d')

# 오른쪽: RPY 시간 기반 그래프
ax2d = fig.add_subplot(122)
ax2d.set_title("Roll, Pitch, Yaw Over Time")
ax2d.set_xlabel("Time (frames)")
ax2d.set_ylabel("Angle (°)")
ax2d.set_ylim([-180, 180])
r_line, = ax2d.plot([], [], label="Roll", color='r')
p_line, = ax2d.plot([], [], label="Pitch", color='g')
y_line, = ax2d.plot([], [], label="Yaw", color='b')
ax2d.legend()

# 버퍼 설정
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

def draw_3d(R):
    ax3d.clear()
    ax3d.set_title("MPU9250 Orientation")
    ax3d.set_xlim([-1, 1])
    ax3d.set_ylim([-1, 1])
    ax3d.set_zlim([-1, 1])
    ax3d.set_xlabel("X (Roll)")
    ax3d.set_ylabel("Y (Pitch)")
    ax3d.set_zlabel("Z (Yaw)")

    origin = np.array([0, 0, 0])
    length = 0.7
    x_axis = R @ np.array([length, 0, 0])
    y_axis = R @ np.array([0, length, 0])
    z_axis = R @ np.array([0, 0, length])
    ax3d.quiver(*origin, *x_axis, color='r', label='X')
    ax3d.quiver(*origin, *y_axis, color='g', label='Y')
    ax3d.quiver(*origin, *z_axis, color='b', label='Z')

    # 큐브 생성
    s = 0.2
    corners = np.array([
        [-s, -s, -s],
        [+s, -s, -s],
        [+s, +s, -s],
        [-s, +s, -s],
        [-s, -s, +s],
        [+s, -s, +s],
        [+s, +s, +s],
        [-s, +s, +s]
    ])
    rotated = [R @ corner for corner in corners]
    faces = [
        [rotated[i] for i in [0, 1, 2, 3]],
        [rotated[i] for i in [4, 5, 6, 7]],
        [rotated[i] for i in [0, 1, 5, 4]],
        [rotated[i] for i in [2, 3, 7, 6]],
        [rotated[i] for i in [1, 2, 6, 5]],
        [rotated[i] for i in [3, 0, 4, 7]],
    ]
    ax3d.add_collection3d(Poly3DCollection(faces, facecolors='skyblue', edgecolors='k', linewidths=1, alpha=0.6))
    ax3d.legend()

def update_2d():
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

        roll = mpu.get("roll", 0)
        pitch = mpu.get("pitch", 0)
        yaw = mpu.get("yaw", 0)

        # 콘솔 출력
        print(f"Roll={roll:.2f}°, Pitch={pitch:.2f}°, Yaw={yaw:.2f}°")

        # 버퍼 갱신
        roll_buffer.append(roll)
        pitch_buffer.append(pitch)
        yaw_buffer.append(yaw)
        if len(roll_buffer) > BUFFER_SIZE:
            roll_buffer.pop(0)
            pitch_buffer.pop(0)
            yaw_buffer.pop(0)

        # 그래프 업데이트
        R = rotation_matrix(roll, pitch, yaw)
        draw_3d(R)
        update_2d()
        plt.pause(0.05)

    except json.JSONDecodeError:
        print("⚠️ JSON 파싱 실패")
    except Exception as e:
        print("❌ 예외:", e)