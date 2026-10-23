#include <Arduino.h>

#include "arduino_adapter.h"

const char *arduino_adapter_version(void) {
  (void)millis();
  return "0.1.0";
}
