#include <Wire.h>
#include <MPU9250_asukiaaa.h>
#include <math.h>

MPU9250_asukiaaa mySensor;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  mySensor.setWire(&Wire);
  mySensor.beginAccel();  // 가속도 센서 시작
  mySensor.beginGyro();   // 자이로 센서 시작

  delay(1000);
}

void loop() {
  mySensor.accelUpdate();  // 가속도 갱신
  mySensor.gyroUpdate();   // 자이로 갱신

  // 가속도 값 읽기
  float ax = mySensor.accelX();
  float ay = mySensor.accelY();
  float az = mySensor.accelZ();

  // pitch 계산 (단위: 도 °)
  float pitch = atan2(-ax, sqrt(ay * ay + az * az)) * 180.0 / PI;

  // 파이썬 실시간 그래프용 숫자만 출력
  Serial.println(pitch);

  // 시리얼 모니터용 출력
  Serial.print("Pitch: ");
  Serial.print(pitch);
  Serial.print("° → ");
  if (pitch > 10) {
    Serial.println("오르막");
  } else if (pitch < -10) {
    Serial.println("내리막");
  } else {
    Serial.println("평지");
  }

  delay(100);
}
