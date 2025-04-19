import serial
import matplotlib.pyplot as plt
from collections import deque

# 📌 사용 중인 COM 포트로 바꿔줘 (예: 'COM3', 'COM4' 등)
ser = serial.Serial('COM4', 9600, timeout=1)

# 실시간 데이터 저장용 버퍼
max_len = 100
data_buffer = deque([0]*max_len, maxlen=max_len)

# 그래프 초기 설정
plt.ion()  # 인터랙티브 모드 ON
fig, ax = plt.subplots()
line, = ax.plot(data_buffer)
ax.set_ylim(-90, 90)
ax.set_title("보행기 기울기 (Pitch) 실시간 그래프")
ax.set_xlabel("시간")
ax.set_ylabel("기울기 (°도)")

while True:
    try:
        if ser.in_waiting:
            line_data = ser.readline().decode('utf-8').strip()
            try:
                pitch = float(line_data)
                data_buffer.append(pitch)
                line.set_ydata(data_buffer)
                line.set_xdata(range(len(data_buffer)))
                ax.relim()
                ax.autoscale_view(True, True, True)
                plt.pause(0.01)

                # 콘솔에도 출력
                if pitch > 10:
                    print(f"기울기 {pitch:.2f}° → 오르막")
                elif pitch < -10:
                    print(f"기울기 {pitch:.2f}° → 내리막")
                else:
                    print(f"기울기 {pitch:.2f}° → 평지")
            except ValueError:
                pass  # 숫자가 아닐 경우 무시
    except KeyboardInterrupt:
        print("시각화 종료")
        break

ser.close()
