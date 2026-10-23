#include <stdio.h>

#include "common.h"
#include "port.h"

#if defined(ARDUINO)
#include <Arduino.h>

#include "arduino_adapter.h"

void setup(void) {
  (void)printf("%s %s %s\n", common_version(), port_version(),
               arduino_adapter_version());
}

void loop(void) {}

#elif defined(ESP_PLATFORM)
#include "espidf_adapter.h"

extern "C" void app_main(void) {
  (void)printf("%s %s %s\n", common_version(), port_version(),
               espidf_adapter_version());
}

#else
#include "host.h"

int main(void) {
  (void)printf("%s %s %s\n", common_version(), port_version(), host_version());
  return 0;
}
#endif
