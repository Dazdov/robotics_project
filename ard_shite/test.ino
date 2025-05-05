void setup() {
  Serial.begin(9600);
  // Set pins 5 through 10 as outputs
  for (int i = 5; i < 11; i++) {
    pinMode(i, OUTPUT);
  }
}

// Speed boost kept at 2x but inputs adjusted to prevent overflow
void speedMotor(int leftSpeed, int rightSpeed) {
  // Apply 2x speed boost (now using lower input values)
  leftSpeed = leftSpeed * 2;
  rightSpeed = rightSpeed * 2;
  
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

// PWM-based speed control with faster timing
void reducedSpeedMotor(int leftSpeed, int rightSpeed, int duration) {
  unsigned long startTime = millis();
  const int pwmInterval = 50; // Faster PWM cycle (50ms instead of 100ms)
  
  while (millis() - startTime < duration) {
    // Apply power for 70% of cycle (was 33%)
    speedMotor(leftSpeed, rightSpeed);
    delay(35); // 70% of 50ms
    
    // Cut power for 30% of cycle
    stopMotors();
    delay(15); // 30% of 50ms
  }
  stopMotors();
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Movement commands with higher base speeds
    switch(command) {
      case '1':  // Faster forward
        reducedSpeedMotor(120, 120, 100); // Was (100,100,100)
        break;
        
      case '2':  // Sharper right turn
        reducedSpeedMotor(80, 0, 100); // Was (60,0,100)
        break;
        
      case '3':  // Sharper left turn
        reducedSpeedMotor(0, 80, 100); // Was (0,60,100)
        break;
    }
  }
}
