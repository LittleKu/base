#include "build/build_config.h"

#include "base/at_exit.h"
#include "base/command_line.h"
#include "base/files/file_path.h"
#include "base/files/file_util.h"
#include "base/logging.h"
#include "base/memory/ptr_util.h"
#include "base/path_service.h"
#include "build/build_config.h"

#if BUILDFLAG(IS_WIN)
#include <atlbase.h>
#endif

#if BUILDFLAG(IS_WIN)
int WINAPI wWinMain(HINSTANCE instance,
                    HINSTANCE prev_instance,
                    LPWSTR command_line,
                    int cmd_show) {
  // on windows call ParseFromString(::GetCommandLineW());
  base::CommandLine::Init(0, nullptr);
#else
int main(int argc, char** argv) {
  // otherwise call InitFromArgv(argc, argv);
  base::CommandLine::Init(argc, argv);
#endif

  base::AtExitManager exit_manager;

  logging::LoggingSettings logging_settings;
  logging_settings.logging_dest = logging::LOG_DEFAULT;

#if BUILDFLAG(IS_WIN)  // on windows LOG_DEFAULT is LOG_TO_FILE
  base::FilePath log_file_path;
  if (logging_settings.logging_dest & logging::LOG_TO_FILE) {
    base::PathService::Get(base::FILE_EXE, &log_file_path);
    log_file_path = log_file_path.RemoveExtension().AddExtension(L".log");
    logging_settings.log_file_path = log_file_path.value().c_str();
  }
#endif

  {
    base::FilePath log_prefix;
    base::PathService::Get(base::FILE_EXE, &log_prefix);
    logging::SetLogPrefix(
        log_prefix.RemoveExtension().BaseName().AsUTF8Unsafe().c_str());
  }

  logging::SetLogItems(true, true, true, true);
  logging::InitLogging(logging_settings);

  LOG(INFO) << "test info log.";
  return 0;
}