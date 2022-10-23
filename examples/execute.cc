#include "base/at_exit.h"
#include "base/command_line.h"
#include "base/files/file_path.h"
#include "base/logging.h"
#include "base/memory/ptr_util.h"
#include "base/path_service.h"

int main(int argc, char** argv) {
  base::CommandLine::Init(argc, argv);

  base::AtExitManager exit_manager;

  logging::LoggingSettings logging_settings;
  logging_settings.logging_dest = logging::LOG_DEFAULT;

  logging::InitLogging(logging_settings);

  LOG(INFO) << "test info log.";
  return EXIT_SUCCESS;
}