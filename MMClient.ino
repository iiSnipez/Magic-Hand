#include <ESP8266WiFi.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_LSM9DS0.h>

// Connect to a network 
const char* ssid     = "MMServer";
const char* password = "MMServer-Password";
 
// IP and port of the server which will receive data
const char* host = "149.160.251.3";
const int port = 12347;
bool connected = false;

// Initialize motion detector
Adafruit_LSM9DS0 lsm = Adafruit_LSM9DS0(1000);

WiFiClient client;

// Setup WiFi connection, and connect to the server
void setup() {
  Serial.begin(9600);
  delay(100);

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  // Start WiFi
  WiFi.begin(ssid, password);
  
  // Connecting...
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  // Successfully connected to WiFi
  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  #ifndef ESP8266
    while(!Serial);
  #endif
    Serial.begin(9600);
    Serial.println("Sensor Test");

  // Initialize the sensor
  if(!lsm.begin())
  {
    // There was a problem detecting the LSM9DS0
    Serial.print(F("Ooops, no LSM9DS0 detected ... Check your wiring or I2C ADDR!"));
    while(1);
  }
  Serial.println(F("Found LSM9DS0 9DOF"));
  
  // Begin connecting to server
  Serial.print("Connecting to ");
  Serial.println(host);

  // Check for successful connection. If failed then abort
  if (!client.connect(host, port)) {
    Serial.println("connection failed");
    connected = false;
    return;
  } else {
    connected = true;
  }

  //Setup the sensor gain and integration time
  configureSensor();
  
  // Display some basic information
  displaySensorDetails();
  
}
 
void loop() {
  delay(250);
  if(connected){
    // This will send data to the server
    sensors_event_t accel, mag, gyro, temp;
    lsm.getEvent(&accel, &mag, &gyro, &temp);
  
    String numbers;
    numbers += accel.acceleration.z;
    numbers += ":";
    numbers += mag.magnetic.y;
    numbers += ":";
    numbers += mag.magnetic.z;
    Serial.print(numbers);
    client.print(numbers);
    Serial.println();
  } else {
    establishConnection();
  }
}

void establishConnection(){
  if (!client.connect(host, port)) {
    Serial.println("connection failed");
    connected = false;
    return;
  } else {
    connected = true;
  }
}

void displaySensorDetails(void)
{
  sensor_t accel, mag, gyro, temp;
  
  lsm.getSensor(&accel, &mag, &gyro, &temp);
  
  Serial.println(F("------------------------------------"));
  Serial.print  (F("Sensor:       ")); Serial.println(accel.name);
  Serial.print  (F("Driver Ver:   ")); Serial.println(accel.version);
  Serial.print  (F("Unique ID:    ")); Serial.println(accel.sensor_id); 
  Serial.println(F("------------------------------------"));
  Serial.println(F(""));
  
  delay(500);
}

void configureSensor(void)
{
  // Set the accelerometer range
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_2G);
  lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_4G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_6G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_8G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_16G);
  
  // Set the magnetometer sensitivity
  //lsm.setupMag(lsm.LSM9DS0_MAGGAIN_2GAUSS);
  //lsm.setupMag(lsm.LSM9DS0_MAGGAIN_4GAUSS);
  //lsm.setupMag(lsm.LSM9DS0_MAGGAIN_8GAUSS);
  lsm.setupMag(lsm.LSM9DS0_MAGGAIN_12GAUSS);

  // Setup the gyroscope
  lsm.setupGyro(lsm.LSM9DS0_GYROSCALE_245DPS);
  //lsm.setupGyro(lsm.LSM9DS0_GYROSCALE_500DPS);
  //lsm.setupGyro(lsm.LSM9DS0_GYROSCALE_2000DPS);
}

