// 3-axis Accelerometer
// SMicroelectronics IIS3DHH 
// Arduino Nano

// IIS3DHH Initilization
#include <SPI.h>

#define SS D0//5 // Serial Select -> CS on IIS3DHH
#define MOSI D10//23 // MasterOutSlaveIn -> SDI
#define MISO D9//19 // MasterInSlaveOut -> SDO
#define SCK D8//18 // Serial Clock -> SPC on IIS3DHH

#define SCALE_I 0.076294;
// scale factor: +/- 2.5G full range = 5000mG total range / 65536 counts (16 bit)
int n = 25; // number of samples
int x_I,y_I,z_I;  // the sensor values
int i = 0;
int j = 0;

const float a = 0.6;

double xA_I, yA_I, zA_I;
double rz_I;


unsigned long now;
unsigned long starttime1 = 0;

void setup() {
  
  pinMode(SS, OUTPUT);
  digitalWrite(SS,HIGH);
  Serial.begin(115200);
  Serial.println("Hello");
// Serial.begin(9600);
//  SPI.begin(18,19,23,5);
// IIS3DHH Initilization
  SPI.begin(SCK,MISO,MOSI,SS);
  Accelerometer_Setup();
  delay(1000);
  readValWho_Am_I();
  
delay(1000);
}

void loop() {
  
  now = micros();
  if(now - starttime1 > 1000){// ここの数字を変えるとサンプリング周期を変更できる（microsなのでマイクロ秒 10^-6）
// IIS3DHH read values
  // double zMin_I = 32767;  // minimum sensor value
  // double zMax_I = -32767;     // maximum sensor value
  // float zTotal_I = 0;
  // float zAvg_I = 0;

  
  readVal(); // get acc values and put into global variables
  
// Print ISS3DHH values    
  // Serial.print(xA_I, 2);
  // Serial.print('\t');
  // Serial.print(",");
  // Serial.print(yA_I, 2);
  // Serial.print('\t');
  // Serial.print(",");
  Serial.println((rz_I*a + zA_I*(1-a)), 2);
  rz_I = zA_I;
  starttime1 = now;
  }
// Adjust for sampling rate (e.g. 10mS = 100Hz. 2mS = 500Hz etc.)

}

//=========== READ IIS3DHHC REGISTERS ==========
void readVal()
{
byte xAddressByteL = 0x28; // Low Byte of X value (the first data register)
byte readBit = B10000000; // bit 0 (MSB) HIGH means read register, 
byte dataByte = xAddressByteL | readBit;
byte b0 = 0x0; // an empty byte to initiate read register
//Serial.println("read request:");
//Serial.println(dataByte);

SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE3));
digitalWrite(SS, LOW); // SS must be LOW to communicate
//delay(10);
SPI.transfer(dataByte); // request a read, starting at X low byte
byte xL = SPI.transfer(b0); // get the low byte of X data
byte xH = SPI.transfer(b0); // get the high byte of X data
byte yL = SPI.transfer(b0); // get the low byte of Y data
byte yH = SPI.transfer(b0); // get the high byte of Y data
byte zL = SPI.transfer(b0); // get the low byte of Z data
byte zH = SPI.transfer(b0); // get the high byte of Z data
//delay(10);
digitalWrite(SS, HIGH);
SPI.endTransaction();

// shift the high byte left 8 bits and merge the high and low
// int xVal = (xL | (xH << 8));
// int yVal = (yL | (yH << 8));
int zVal = (zL | (zH << 8));

// scale the values into mG
// xA_I = xVal * SCALE_I;
// yA_I = yVal * SCALE_I;
zA_I = zVal * SCALE_I;
}

//=========== SETUP IIS3DHHC ==========
void Accelerometer_Setup()
{

// write to Control register 1: address 20h
byte addressByte = 0x20;
byte ctrlRegByte = 0xC0; // 0xC0 = 1100 0000 : normal mode, incremented addressing // 0x80 = normal mode, do not increment

SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE3));
digitalWrite(SS, LOW);
delay(10);
SPI.transfer(addressByte);
SPI.transfer(ctrlRegByte);
delay(10);
digitalWrite(SS, HIGH);
SPI.endTransaction();

delay(100);

// write to Control Register 4: address 23h
addressByte = 0x23;
// This register configures filter and bandwidth
ctrlRegByte = 0x00; // FIR Linear Phase, 440Hz

SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE3));
digitalWrite(SS, LOW);
delay(10);
SPI.transfer(addressByte);
SPI.transfer(ctrlRegByte);
delay(10);
digitalWrite(SS, HIGH);
SPI.endTransaction();

delay(1000);
}

//=========== READ Who_Am_I REGISTER ==========
void readValWho_Am_I()
{
byte xAddressByteL = 0x0F; // Address of Who_Am_I register
byte readBit = B10000000; // bit 0 (MSB) HIGH means read register, 
byte dataByte = xAddressByteL | readBit;
byte b0 = 0x0; // an empty byte to initiate read register
//Serial.println("read request:");
//Serial.println(dataByte);

SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE3));
digitalWrite(SS, LOW); // SS must be LOW to communicate
//delay(10);
byte xH = SPI.transfer(dataByte); // request a read, starting at X low byte
byte xL = SPI.transfer(b0); // get the low byte of X data

Serial.println(xH);
Serial.println(xL);

//delay(10);
digitalWrite(SS, HIGH);
SPI.endTransaction();

// Serial.print("Who_Am_I = ");
// Serial.println(xL);
}