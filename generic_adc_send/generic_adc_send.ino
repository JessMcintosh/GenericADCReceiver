#define NUM_CHANNELS 4
//#define DEBUG

int adcpin[NUM_CHANNELS] = {0,1,2,3};

void setup() {
  Serial.begin(115200);
  for(int i = 0; i < NUM_CHANNELS; i++){
    pinMode(i, INPUT);
  }
}

uint16_t value = 0;
uint16_t mask = B11111111;
uint8_t first_half;
uint8_t second_half;

boolean pause = 1;

void loop() {

  if(Serial.available() > 0){
    Serial.read();
    pause = !pause;
  }

  if(pause){
    delay(200);
    return;
  }
  
  #ifndef DEBUG
  Serial.write((byte)0xBE);
  Serial.write((byte)0xEF);
  #endif
  
  for(int i = 0; i < NUM_CHANNELS; i++){
    
    value = analogRead(adcpin[i]);
    first_half = value >> 8;
    second_half = value & mask;

    #ifndef DEBUG
    //Serial.write((byte)i);
    Serial.write(second_half);
    Serial.write(first_half);
    #else
    Serial.println(i);
    Serial.println(value);
    #endif
    
    //Serial.println("");
  }
  delay(10);
}
