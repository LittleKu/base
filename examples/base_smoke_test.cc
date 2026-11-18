#include <atomic>
#include <string>

#include "base/at_exit.h"
#include "base/check.h"
#include "base/check_op.h"
#include "base/command_line.h"
#include "base/feature_list.h"
#include "base/files/file_path.h"
#include "base/files/file_util.h"
#include "base/files/scoped_temp_dir.h"
#include "base/functional/bind.h"
#include "base/json/json_reader.h"
#include "base/json/json_writer.h"
#include "base/location.h"
#include "base/logging.h"
#include "base/logging/logging_settings.h"
#include "base/run_loop.h"
#include "base/task/single_thread_task_executor.h"
#include "base/task/single_thread_task_runner.h"
#include "base/task/task_traits.h"
#include "base/task/thread_pool.h"
#include "base/task/thread_pool/thread_pool_instance.h"
#include "base/time/time.h"
#include "base/timer/timer.h"
#include "base/values.h"
#include "base/version.h"
#include "base/version_info/version_info.h"

int main(int argc, char** argv) {
  base::AtExitManager exit_manager;
  CHECK(base::CommandLine::Init(argc, argv));
  CHECK(base::FeatureList::InitInstance("", ""));
  logging::LoggingSettings logging_settings;
  logging_settings.logging_dest = logging::LOG_TO_STDERR;
  CHECK(logging::InitLogging(logging_settings));
  CHECK(version_info::GetVersion().IsValid());

  base::ScopedTempDir temp_dir;
  CHECK(temp_dir.CreateUniqueTempDir());
  const auto path = temp_dir.GetPath().AppendASCII("smoke.json");
  constexpr char kJson[] = R"({"answer":42,"message":"base smoke test"})";
  CHECK(base::WriteFile(path, kJson));
  std::string contents;
  CHECK(base::ReadFileToString(path, &contents));
  CHECK_EQ(contents, kJson);
  auto parsed = base::JSONReader::ReadDict(contents, base::JSON_PARSE_RFC);
  CHECK(parsed);
  CHECK(parsed->FindInt("answer") == 42);
  const auto* message = parsed->FindString("message");
  CHECK(message);
  CHECK_EQ(*message, "base smoke test");
  auto serialized = base::WriteJson(*parsed);
  CHECK(serialized);
  auto round_trip =
      base::JSONReader::ReadDict(*serialized, base::JSON_PARSE_RFC);
  CHECK(round_trip);
  CHECK(*parsed == *round_trip);
  CHECK(!base::JSONReader::Read("{", base::JSON_PARSE_RFC));
  CHECK(temp_dir.Delete());

  base::SingleThreadTaskExecutor task_executor;
  base::ThreadPoolInstance::CreateAndStartWithDefaultParams("BaseSmokeTest");
  base::RunLoop run_loop;
  base::OneShotTimer timeout;
  timeout.Start(FROM_HERE, base::Seconds(30), base::BindOnce([] {
                  CHECK(false) << "Timed out waiting for the thread pool reply";
                }));
  int reply_result = 0;
  CHECK(base::ThreadPool::PostTaskAndReplyWithResult(
      FROM_HERE, base::BindOnce([] { return 42; }),
      base::BindOnce(
          [](int* reply_result, base::RepeatingClosure quit, int result) {
            CHECK(base::SingleThreadTaskRunner::HasCurrentDefault());
            *reply_result = result;
            quit.Run();
          },
          base::Unretained(&reply_result), run_loop.QuitClosure())));
  run_loop.Run();
  CHECK_EQ(reply_result, 42);
  timeout.Stop();

  std::atomic<bool> shutdown_task_completed = false;
  CHECK(base::ThreadPool::PostTask(
      FROM_HERE, {base::TaskShutdownBehavior::BLOCK_SHUTDOWN},
      base::BindOnce(
          [](std::atomic<bool>* completed) { completed->store(true); },
          base::Unretained(&shutdown_task_completed))));
  base::ThreadPoolInstance::Get()->Shutdown();
  CHECK(shutdown_task_completed.load());
  base::ThreadPoolInstance::Get()->JoinForTesting();
  LOG(INFO) << "base smoke test passed (Chromium "
            << version_info::GetVersionNumber() << ")";
  return 0;
}
