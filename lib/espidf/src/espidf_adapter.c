#include <esp_err.h>

#include "espidf_adapter.h"

const char *espidf_adapter_version(void) {
  (void)esp_err_to_name(ESP_OK);
  return "0.1.0";
}
