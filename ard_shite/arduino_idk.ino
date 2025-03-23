void setup() {
  Serial.begin(9600);
  for (int i = 5; i < 11; i++) {
    pinMode(i, OUTPUT);
  }
}

void speedMotor(int left, int right) {
  if (right >= 0) {
    digitalWrite(8, HIGH);
    digitalWrite(9, LOW);
    analogWrite(10, right * 2.55);
  } else {
    right = -right;
    digitalWrite(8, LOW);
    digitalWrite(9, HIGH);
    analogWrite(10, right * 2.55);
  }

  if (left >= 0) {
    digitalWrite(6, HIGH);
    digitalWrite(7, LOW);
    analogWrite(5, left * 2.55);
  } else {
    left = -left;
    digitalWrite(6, LOW);
    digitalWrite(7, HIGH);
    analogWrite(5, left * 2.55);
  }
}

void stopMotors() {
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  analogWrite(10, 0);
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  analogWrite(5, 0);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == '1') {
      speedMotor(54, 40);
      delay(100);
      stopMotors();
    } else if (command == '2') {
      speedMotor(27, 0);
      delay(100);
      stopMotors();
    } else if (command == '3') {
      speedMotor(0, 20);
      delay(100);
      stopMotors();
    }
  }
}
