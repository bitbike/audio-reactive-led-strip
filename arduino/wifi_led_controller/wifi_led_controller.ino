#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <FastLED.h>

// THIS PROJECT USES THE FASTLED-LIBRARY
// FOR FURTHER INFORMATION LOOK AT https://github.com/FastLED/FastLED
// THERE WILL BE EXAMPLES HOW TO USE THE LIBRARAY WITH YOUR DEVICE/LED

// Fixed definitions cannot change on the fly.
#define LED_DT 5        // Serial data pin
#define COLOR_ORDER BRG // It's GRB for WS2812B | BGR for APA102 | BRG for WS2811
#define LED_TYPE WS2811 // What kind of strip are you using (APA102, WS2801 or WS2812B)?
#define NUM_LEDS 99     // Number of LED's
#define BUFFER_LEN 1024 // Maximum number of packets to hold in the buffer. Don't change this.
#define PRINT_FPS 1     // Toggles FPS output (1 = print FPS over serial, 0 = disable output)
#define USE_DHCP 1      // Toggles the use of DHCP or static config

// Wifi and network settings
const char *ssid = "YOUR_WIFI_SSID";
const char *password = "YOUR_WIFI_PASSWORD";
const char *hostname = "YOUR_ESP_HOST_NAME";
#if !USE_DHCP
IPAddress ip(192, 168, 0, 150);     // IP must match the IP in config.py
IPAddress gateway(192, 168, 0, 1);  // Set gateway to your router's gateway
IPAddress subnet(255, 255, 255, 0); // Subnet must match your router's subnet
#endif

//ESP Listening Port and buffersize
unsigned int localPort = 7777;
char packetBuffer[BUFFER_LEN];

// Initialize changeable global variables.
uint8_t max_bright = 255;     // Overall brightness definition. It can be changed on the fly.
struct CRGB pixels[NUM_LEDS]; // Initialize our LED array.
WiFiUDP port;                 // UDP Port for Data packages

void setup()
{
    Serial.begin(115200);
#if !USE_DHCP
    WiFi.config(ip, gateway, subnet);
#endif
    WiFi.begin(ssid, password);

    Serial.println(""); // Just to make serial look beatiful
    Serial.print("Connecting.");

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        WiFi.hostname(hostname);
    }

    Serial.println("");
    Serial.print("Connected to ");
    Serial.println(ssid);
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Hostname: ");
    Serial.println(hostname);

    port.begin(localPort);

    // Initialize LED Strip with FastLED library.
    LEDS.addLeds<LED_TYPE, LED_DT, COLOR_ORDER>(pixels, NUM_LEDS); // For WS2811
    FastLED.setBrightness(max_bright);                             // For maximum brightness
    set_max_power_in_volts_and_milliamps(5, 500);                  // FastLED Power management set at 5V, 500mA
}

uint8_t N = 0;
#if PRINT_FPS
uint16_t fpsCounter = 0;
uint32_t secondTimer = 0;
#endif

void loop()
{
    // Read data over socket
    int packetSize = port.parsePacket();
    // If packets have been received, interpret the command
    if (packetSize)
    {
        int len = port.read(packetBuffer, BUFFER_LEN);
        for (int i = 0; i < len; i += 4)
        {
            packetBuffer[len] = 0;
            N = packetBuffer[i];
            pixels[N].r = (uint8_t)packetBuffer[i + 1];
            pixels[N].g = (uint8_t)packetBuffer[i + 2];
            pixels[N].b = (uint8_t)packetBuffer[i + 3];
        }
        FastLED.show();
#if PRINT_FPS
        fpsCounter++;
#endif
    }
#if PRINT_FPS
    if (millis() - secondTimer >= 1000U)
    {
        secondTimer = millis();
        Serial.printf("FPS: %d\n", fpsCounter);
        fpsCounter = 0;
    }
#endif
}
