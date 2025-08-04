void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);  // D4
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');

    if (command == "LED_ON") {
      digitalWrite(LED_BUILTIN, LOW);  // Active LOW
      Serial.println("LED is ON");
    } else if (command == "LED_OFF") {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("LED is OFF");
    } else if (command == "READ_ADC") {
      int adcValue = analogRead(A0); // You may use a voltage divider if needed
      Serial.println(String(adcValue));
    }
  }

  delay(100); // Small delay
}
