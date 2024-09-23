#define NUM_CHANNELS 4
#define SAMPLE_RATE 1000 // Hz

const int channelPins[NUM_CHANNELS] = {A0, A1, A2, A3};
unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(115200);
  // ADC resolution is 10-bit by default (0-1023 range)
}

void loop() {
  if (micros() - lastSampleTime >= 1000000 / SAMPLE_RATE) {
    lastSampleTime = micros();
    
    for (int i = 0; i < NUM_CHANNELS; i++) {
      int sensorValue = analogRead(channelPins[i]);
      Serial.print(sensorValue);
      if (i < NUM_CHANNELS - 1) {
        Serial.print(",");
      }
    }
    Serial.println();
  }
}