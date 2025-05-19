void setup() {
  Serial.begin(9600);
  // Set pins 5 through 10 as outputs
  for (int i = 5; i < 11; i++) {
    pinMode(i, OUTPUT);
  }
}

// Modified speedMotor function with 50% speed increase
void speedMotor(int leftSpeed, int rightSpeed) {
  // Apply 50% speed boost to all values
  leftSpeed = leftSpeed * 2.55;
  rightSpeed = rightSpeed * 2.55;
  
  // Constrain values to prevent overflow (max 255 PWM value)
  leftSpeed = constrain(leftSpeed, -255, 255);
  rightSpeed = constrain(rightSpeed, -255, 255);
  
  // Right motor control (pins 8, 9, 10)
  if (rightSpeed >= 0) {
    digitalWrite(8, HIGH);
    digitalWrite(9, LOW);
    analogWrite(10, abs(rightSpeed));
  } else {
    digitalWrite(8, LOW);
    digitalWrite(9, HIGH);
    analogWrite(10, abs(rightSpeed));
  }

  // Left motor control (pins 6, 7, 5)
  if (leftSpeed >= 0) {
    digitalWrite(6, HIGH);
    digitalWrite(7, LOW);
    analogWrite(5, abs(leftSpeed));
  } else {
    digitalWrite(6, LOW);
    digitalWrite(7, HIGH);
    analogWrite(5, abs(leftSpeed));
  }
}

void stopMotors() {
  // Right motor stop (pins 8, 9, 10)
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  analogWrite(10, 0);
  
  // Left motor stop (pins 6, 7, 5)
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  analogWrite(5, 0);
}

// PWM-based speed control (now uses the boosted speeds)
void reducedSpeedMotor(int leftSpeed, int rightSpeed, int duration) {
  unsigned long startTime = millis();
  const int pwmInterval = 40; // PWM cycle duration in ms
  
  while (millis() - startTime < duration) {
    // Apply full power for the interval
    speedMotor(leftSpeed, rightSpeed);
    delay(pwmInterval/2);
    
    // Cut power for the other half
    stopMotors();
    delay(pwmInterval/2);
  }
  stopMotors();
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Movement commands (original values, but will be boosted internally)
    switch(command) {
      case '1':  // Forward
        reducedSpeedMotor(100, 100, 100);
        break;
        
      case '2':  // Turn right
        reducedSpeedMotor(60, 0, 100);
        break;
        
      case '3':  // Turn left
        reducedSpeedMotor(0, 60, 100);
        break;
    }
  }
}
