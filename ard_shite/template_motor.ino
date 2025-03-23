


void setup() {
  for (int i = 5; i < 11; i++) {
    pinMode(i, OUTPUT);
  }
}

void speedMotor(int left, int right) {
  if (right >= 0) {
    digitalWrite(8, 1);
    digitalWrite(9, 0);
    analogWrite(10, right * 2.55);
  } else {
    right = -right;
    digitalWrite(8, 0);
    digitalWrite(9, 1);
    analogWrite(10, right * 2.55);
  }

  if (left >= 0) {
    digitalWrite(6, 1);
    digitalWrite(7, 0);
    analogWrite(5, left * 2.55);
  } else {
    left = -left;
    digitalWrite(6, 0);
    digitalWrite(7, 1);
    analogWrite(5, left * 2.55);
  }
}

void loop() {
  speedMotor(50, 50);


  
}


