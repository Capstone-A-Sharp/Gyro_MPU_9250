#include <Wire.h>
#include <MPU9250_asukiaaa.h>
#include <math.h>

MPU9250_asukiaaa mySensor;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  mySensor.setWire(&Wire);
  mySensor.beginAccel();
  mySensor.beginGyro();
  mySensor.beginMag();  // 자기장 사용
  delay(1000);
}

void loop() {
  mySensor.accelUpdate();
  mySensor.gyroUpdate();
  mySensor.magUpdate();

  // 센서 값 읽기
  float ax = mySensor.accelX();
  float ay = mySensor.accelY();
  float az = mySensor.accelZ();

  float gx = mySensor.gyroX();
  float gy = mySensor.gyroY();
  float gz = mySensor.gyroZ();

  float mx = mySensor.magX();
  float my = mySensor.magY();
  float mz = mySensor.magZ();

  // Roll, Pitch 계산 (라디안 → 도)
  float roll  = atan2(ay, az) * 180.0 / PI;
  float pitch = atan2(-ax, sqrt(ay * ay + az * az)) * 180.0 / PI;

  // Yaw 계산 (자기장 기반, tilt 보정 없이 단순 계산)
  float yaw = atan2(my, mx) * 180.0 / PI;
  if (yaw < 0) yaw += 360.0;  // 음수 방지

  // JSON 전송
  Serial.print("{\"MPU9250\":{");

  Serial.print("\"accel\":{");
  Serial.print("\"x\":"); Serial.print(ax, 3); Serial.print(",");
  Serial.print("\"y\":"); Serial.print(ay, 3); Serial.print(",");
  Serial.print("\"z\":"); Serial.print(az, 3); Serial.print("},");

  Serial.print("\"gyro\":{");
  Serial.print("\"x\":"); Serial.print(gx, 3); Serial.print(",");
  Serial.print("\"y\":"); Serial.print(gy, 3); Serial.print(",");
  Serial.print("\"z\":"); Serial.print(gz, 3); Serial.print("},");

  Serial.print("\"mag\":{");
  Serial.print("\"x\":"); Serial.print(mx, 3); Serial.print(",");
  Serial.print("\"y\":"); Serial.print(my, 3); Serial.print(",");
  Serial.print("\"z\":"); Serial.print(mz, 3); Serial.print("},");

  Serial.print("\"roll\":"); Serial.print(roll, 2); Serial.print(",");
  Serial.print("\"pitch\":"); Serial.print(pitch, 2); Serial.print(",");
  Serial.print("\"yaw\":"); Serial.print(yaw, 2);

  Serial.println("}}");
  Serial.println("END");

  delay(100);  // 10Hz 주기
}