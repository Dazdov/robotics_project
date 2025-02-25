void setup() {
  Serial.begin(9600);
  // Set pins 5 through 10 as outputs.
  for (int i = 5; i < 11; i++) {
    pinMode(i, OUTPUT);
  }
}

// This function controls the two motors.
// 'left' and 'right' are speed percentages (0 to 100).
void speedMotor(int left, int right) {
  // Right motor control (pins 8, 9, 10)
  if (right >= 0) {
    digitalWrite(8, HIGH);
    digitalWrite(9, LOW);
    analogWrite(10, right * 2.55);  // 2.55 scales 0-100 to 0-255
  } else {
    right = -right;
    digitalWrite(8, LOW);
    digitalWrite(9, HIGH);
    analogWrite(10, right * 2.55);
  }

  // Left motor control (pins 6, 7, 5)
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

// This function stops both motors.
void stopMotors() {
  // Stop right motor
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  analogWrite(10, 0);

  // Stop left motor
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  analogWrite(5, 0);
}

void loop() {
  // Check if there is data available on the Serial port
  if (Serial.available() > 0) {
    // Read the incoming byte
    char command = Serial.read();

    // Based on the command received, call speedMotor() with the desired speeds.
    if (command == '1') {
      // Soccer ball is centered: move forward
      speedMotor(27 * 0.9, 20 * 0.9);  // Decreased by 30%
      delay(100);  // Move for 10 milliseconds
      stopMotors();  // Stop the motors after 10 milliseconds
    } else if (command == '2') {
      // Soccer ball is to the right: turn right
      speedMotor(27 * 0.9, -20 * 0.9);  // Decreased by 30%
      delay(100);  // Move for 10 milliseconds
      stopMotors();  // Stop the motors after 10 milliseconds
    } else if (command == '3') {
      // Soccer ball is to the left: turn left
      speedMotor(-27 * 0.9, 20 * 0.9);  // Decreased by 30%
      delay(100);  // Move for 10 milliseconds
      stopMotors();  // Stop the motors after 10 milliseconds
    }
  }
}
