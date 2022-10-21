#include "base/at_exit.h"
#include "base/command_line.h"
#include "base/memory/ptr_util.h"

int main(int argc, char **argv) {
    base::CommandLine::Init(argc, argv);

    base::AtExitManager exit_manager;

    return EXIT_SUCCESS;
}