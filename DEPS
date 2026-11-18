# Chromium 158.0.8127.37, selected from the matching upstream DEPS.
# Source: https://chromium.googlesource.com/chromium/src/+/b8c2be851f62f6a394ec57955d7f31335d7cb6d4/DEPS
# scripts/sync_chromium.py imports source directories from the same commit.

use_relative_paths = True

gclient_gn_args_file = 'build/config/gclient_args.gni'
gclient_gn_args = [
  'android_ndk_version',
  'build_with_chromium',
  'checkout_android',
  'checkout_android_prebuilts_build_tools',
  'checkout_clang_coverage_tools',
  'checkout_copybara',
  'checkout_fuchsia',
  'checkout_glic_e2e_tests',
  'checkout_ios_webkit',
  'checkout_mutter',
  'checkout_openxr',
  'checkout_src_internal',
  'checkout_src_internal_infra',
  'checkout_clusterfuzz_data',
  'cros_boards',
  'cros_boards_with_qemu_images',
  'generate_location_tags',
]

vars = {
  'chromium_revision': 'b8c2be851f62f6a394ec57955d7f31335d7cb6d4',
  'android_ndk_version': Str('2@30.0.16248370'),
  'build_with_chromium': True,
  'checkout_android': False,
  'checkout_fuchsia': False,
  'checkout_android_prebuilts_build_tools': False,
  'checkout_clusterfuzz_data': False,
  'checkout_mutter': False,
  'checkout_src_internal': False,
  'checkout_src_internal_infra': False,
  'checkout_glic_e2e_tests': False,
  'checkout_clang_coverage_tools': False,
  'checkout_clang_tidy': False,
  'checkout_clangd': False,
  'checkout_openxr': False,
  'checkout_ios_webkit': False,
  'cros_boards': Str(''),
  'cros_boards_with_qemu_images': Str(''),
  'generate_location_tags': True,
  'checkout_copybara': False,
  'llvm_force_head_revision': False,
  'rust_force_head_revision': False,
  'cpython3_version': 'version:3@3.11.9.chromium.38',
  'boringssl_git': 'https://boringssl.googlesource.com',
  'chromium_git': 'https://chromium.googlesource.com',
  'boringssl_revision': 'ea9f3a34c3977144c45d272be81842fd891a0bdb',
  'googletest_revision': '0b656495436f57212be8700794a3d5fb14000c5f',
  'lss_revision': '29164a80da4d41134950d76d55199ea33fbb9613',
  'harfbuzz_revision': '12ee77ee00514c442bcd28f9aa9d56b708c37382',
  'catapult_revision': '4a6f0659c26fc478756e83f0d007b91ca5f6d36f',
  'libfuzzer_revision': 'c7ea90fb61105752fa78e257e77a7c5d62fff7d3',
  'fuzztest_revision': 'a2d3cb097f07a91dd26768db7d9f0898cd42b0f0',
  'libexpat_revision': 'a851869e111c06fbcdc89edf639abf5fc2b6deba',
  'result_adapter_revision': 'git_revision:5fb3ca203842fd691cab615453f8e5a14302a1d8',
  'libcxxabi_revision': '440f88852530ac197479edb1463dda1916692cce',
  'libunwind_revision': '9e44ea2ff4f53a60c2a3d2b6f511d7bab9ab12f0',
  'llvm_libc_revision': '567c143bea85f11d15702a120561a8e51f46f02c',
  'compiler_rt_revision': 'b8403c8cb61be59a519c3cf63217190c414bdf07',
  'libcxx_revision': '9ba7713d3a0f1e179904c984bb626748b15e57d6',
  'gn_version': 'git_revision:938087829fcbcc8fd87835ee301dd522c7637685',
  'ninja_package': 'infra/3pp/tools/ninja/',
  'ninja_version': 'version:3@1.12.1.chromium.4',
  'non_git_source': 'True',
}

pre_deps_hooks = [{
  'name': 'chromium_source',
  'pattern': '.',
  'action': ['python3', 'scripts/sync_chromium.py', Var('chromium_revision')],
}]

deps = {
  'build/linux/debian_bullseye_amd64-sysroot': {
    'bucket': 'chrome-linux-sysroot',
    'condition': 'checkout_linux and checkout_x64 and non_git_source',
    'dep_type': 'gcs',
    'objects': [
      {
        'generation': 1792192152972543,
        'object_name': 'f851add76bdae472fb6c94b4f920bc4a132d85ac607951391297f636af7e934e',
        'sha256sum': 'f851add76bdae472fb6c94b4f920bc4a132d85ac607951391297f636af7e934e',
        'size_bytes': 19314716,
      },
    ],
  },
  'build/linux/debian_bullseye_arm64-sysroot': {
    'bucket': 'chrome-linux-sysroot',
    'condition': 'checkout_linux and checkout_arm64 and non_git_source',
    'dep_type': 'gcs',
    'objects': [
      {
        'generation': 1792192630237696,
        'object_name': '278c36fe3a785d7f89fbe3f46956899a3bd49fe665f68dc667d6f626a951fcd6',
        'sha256sum': '278c36fe3a785d7f89fbe3f46956899a3bd49fe665f68dc667d6f626a951fcd6',
        'size_bytes': 18015920,
      },
    ],
  },
  'build/linux/debian_bullseye_i386-sysroot': {
    'bucket': 'chrome-linux-sysroot',
    'condition': 'checkout_linux and (checkout_x86 or checkout_x64) and non_git_source',
    'dep_type': 'gcs',
    'objects': [
      {
        'generation': 1792192792939606,
        'object_name': '854e63992a633c8d54b69959d7b789453239d7f4bc30216594f0e3eb1b520402',
        'sha256sum': '854e63992a633c8d54b69959d7b789453239d7f4bc30216594f0e3eb1b520402',
        'size_bytes': 19375240,
      },
    ],
  },
  'third_party/llvm-build/Release+Asserts': {
    'dep_type': 'gcs',
    'bucket': 'chromium-browser-clang',
    'condition': 'not llvm_force_head_revision',
    'objects': [
      {
        'object_name': 'Linux_x64/clang-android-runtime-library-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': 'dd03492cad72f223d7743c2f4af39c405f5bac7f7f342de09697a45b7108ce4e',
        'size_bytes': 6188284,
        'generation': 1792086693754706,
        'condition': 'checkout_android and non_git_source',
      },
      {
        'object_name': 'Linux_x64/clang-linux-runtime-library-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '38338f434311fcd12a070757c23830d6076529f4dcbefebc9d094804dc4eca63',
        'size_bytes': 3145380,
        'generation': 1792086698521278,
        'condition': 'checkout_linux and not host_os == "linux"',
      },
      {
        'object_name': 'Linux_x64/clang-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '0b76afc1a29b0583f7723e966b9b65a22b15d8fdcd38e7c567ae32343c68944d',
        'size_bytes': 58394648,
        'generation': 1792086691304470,
        'condition': 'host_os == "linux" and non_git_source',
      },
      {
        'object_name': 'Linux_x64/clang-tidy-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': 'cf2a7610086b45fb878f606709babd3cbd8e26ea97a087ea47929e4ee871b562',
        'size_bytes': 15213064,
        'generation': 1792086691338093,
        'condition': 'host_os == "linux" and checkout_clang_tidy and non_git_source',
      },
      {
        'object_name': 'Linux_x64/clangd-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '5ef64ed6fdeab8dfd91f11db07c601ce5107fc9e61e9d7a18dcee97af42f03c6',
        'size_bytes': 15595776,
        'generation': 1792086691391942,
        'condition': 'host_os == "linux" and checkout_clangd and non_git_source',
      },
      {
        'object_name': 'Linux_x64/llvm-code-coverage-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '756e08684179166571dd155471e0a9c4525223d30b45d776b3d75a4d53b820d3',
        'size_bytes': 2432768,
        'generation': 1792086691721951,
        'condition': 'host_os == "linux" and checkout_clang_coverage_tools and non_git_source',
      },
      {
        'object_name': 'Linux_x64/llvmobjdump-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '2282c8a4bdc6e12242989525039a36e7eeb4335b22d39d3b5d624c38083881c5',
        'size_bytes': 6011380,
        'generation': 1792086691439732,
        'condition': '((checkout_linux or checkout_mac or checkout_ios or checkout_android) and host_os == "linux") and non_git_source',
      },
      {
        'object_name': 'Mac/clang-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': 'ae29ec360eda6e80e96f8638d368ecdeea93d19c18c527c525dc0932bd5243a4',
        'size_bytes': 54834700,
        'generation': 1792086700293656,
        'condition': 'host_os == "mac" and host_cpu == "x64"',
      },
      {
        'object_name': 'Mac/clang-mac-runtime-library-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': 'c18444eef64cf27a8913ce73ffa8fd92e6f41306a02bbc82d805aa0c521863e0',
        'size_bytes': 997164,
        'generation': 1792086707123823,
        'condition': '(checkout_mac or checkout_ios) and not host_os == "mac"',
      },
      {
        'object_name': 'Mac/clang-tidy-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '3997f34e72dc28eb30af1b8af903ceb6b0f516db7821996297bf296793addc72',
        'size_bytes': 14437076,
        'generation': 1792086700400707,
        'condition': 'host_os == "mac" and host_cpu == "x64" and checkout_clang_tidy',
      },
      {
        'object_name': 'Mac/clangd-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '0fc9c351ad3bc6c357cc53a57dad6f8ebf45ba9e38150012cb457812f2a1314f',
        'size_bytes': 15359244,
        'generation': 1792086700318835,
        'condition': 'host_os == "mac" and host_cpu == "x64" and checkout_clangd',
      },
      {
        'object_name': 'Mac/llvm-code-coverage-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': 'b8b2f099cb029ff36cce33c9983984f547d7da0d9c34c1b427bb1080a31b8047',
        'size_bytes': 2307268,
        'generation': 1792086700464636,
        'condition': 'host_os == "mac" and host_cpu == "x64" and checkout_clang_coverage_tools',
      },
      {
        'object_name': 'Mac/llvmobjdump-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': 'eae7800773f3955fd1dcc334d8779b9a232ca6ebd3a79a55be028bd8797b1197',
        'size_bytes': 5586688,
        'generation': 1792086700364844,
        'condition': 'host_os == "mac" and host_cpu == "x64"',
      },
      {
        'object_name': 'Mac_arm64/clang-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '0a8d887534b3153c7f6860265dc7e075d420174521c60ccd52c2c243949ef468',
        'size_bytes': 44917408,
        'generation': 1792086708845653,
        'condition': 'host_os == "mac" and host_cpu == "arm64"',
      },
      {
        'object_name': 'Mac_arm64/clang-tidy-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '1aee3a0078bbe3b840125f521d3e6d985de61531ee6686a0bef80abc6e6d6a78',
        'size_bytes': 12291060,
        'generation': 1792086708806950,
        'condition': 'host_os == "mac" and host_cpu == "arm64" and checkout_clang_tidy',
      },
      {
        'object_name': 'Mac_arm64/clangd-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '799e034e1fdff7eb7d899329ab20bbeb96642234844c9e070797059bd6ce5ee9',
        'size_bytes': 12292508,
        'generation': 1792086709015693,
        'condition': 'host_os == "mac" and host_cpu == "arm64" and checkout_clangd',
      },
      {
        'object_name': 'Mac_arm64/llvm-code-coverage-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': 'a77bacfb3e6c08af7d51981d88fb4aa07e4fb797f37937071dd8657b7c2dea8e',
        'size_bytes': 1897140,
        'generation': 1792086709049271,
        'condition': 'host_os == "mac" and host_cpu == "arm64" and checkout_clang_coverage_tools',
      },
      {
        'object_name': 'Mac_arm64/llvmobjdump-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '8d15119ffd7e9d52e86676bfdcfd8159506f0ba6c4b292ae4112cbf15e629d7d',
        'size_bytes': 5269524,
        'generation': 1792086709009144,
        'condition': 'host_os == "mac" and host_cpu == "arm64"',
      },
      {
        'object_name': 'Win/clang-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '08abce6e1d01c2fff9b25a09e36d9976296f27842196f96411b8220364481818',
        'size_bytes': 52783904,
        'generation': 1792086718487613,
        'condition': 'host_os == "win"',
      },
      {
        'object_name': 'Win/clang-tidy-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': 'ee25e107e6da91254780b0e9b6fb34198dc03636330c5564a7786e6450916d45',
        'size_bytes': 15436080,
        'generation': 1792086718412245,
        'condition': 'host_os == "win" and checkout_clang_tidy',
      },
      {
        'object_name': 'Win/clang-win-runtime-library-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': 'a156f6fa1f149e45faa683f2b2d1cc010df1e29912b3cb0a0dd3e3d9186c513b',
        'size_bytes': 2707764,
        'generation': 1792086725161419,
        'condition': 'checkout_win and not host_os == "win"',
      },
      {
        'object_name': 'Win/clangd-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '0db39ead1a1f49137570fd5e99ab7520262c2e6444900b551862ae2cccdf6bb8',
        'size_bytes': 15910376,
        'generation': 1792086718402867,
       'condition': 'host_os == "win" and checkout_clangd',
      },
      {
        'object_name': 'Win/llvm-code-coverage-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '3cfd8304148bd6bdd86a99f4e5f01ea2b4fbcbf4f35e29a2ca3cb235cb88c393',
        'size_bytes': 2604364,
        'generation': 1792086718581883,
        'condition': 'host_os == "win" and checkout_clang_coverage_tools',
      },
      {
        'object_name': 'Win/llvmobjdump-llvmorg-24-init-14453-ge063be79-1.tar.xz',
        'sha256sum': '3b58242027a9e86114d05444e9e70a9ed497a6a9e9c14d1b86c355e140503a53',
        'size_bytes': 6123208,
        'generation': 1792086718463583,
        'condition': '(checkout_linux or checkout_mac or checkout_android) and host_os == "win"',
      },
    ]
  },
  'third_party/rust-toolchain': {
    'dep_type': 'gcs',
    'bucket': 'chromium-browser-clang',
    'condition': 'not rust_force_head_revision',
    'objects': [
      {
        'object_name': 'Linux_x64/rust-toolchain-8a9dd7abdf013ec10cfeaaa3685feba18ef1c90c-1-llvmorg-24-init-14453-ge063be79.tar.xz',
        'sha256sum': '3f62ea86b027923b1fce17ac2ef002d1788b608245003440b46558a8e735b83d',
        'size_bytes': 287328068,
        'generation': 1792086676135089,
        'condition': 'host_os == "linux" and non_git_source',
      },
      {
        'object_name': 'Mac/rust-toolchain-8a9dd7abdf013ec10cfeaaa3685feba18ef1c90c-1-llvmorg-24-init-14453-ge063be79.tar.xz',
        'sha256sum': '54d1db81fbbc7a97387b3cc9192a3497eea096c258ccae8f94fa46b5dac463c8',
        'size_bytes': 274448924,
        'generation': 1792086679706753,
        'condition': 'host_os == "mac" and host_cpu == "x64"',
      },
      {
        'object_name': 'Mac_arm64/rust-toolchain-8a9dd7abdf013ec10cfeaaa3685feba18ef1c90c-1-llvmorg-24-init-14453-ge063be79.tar.xz',
        'sha256sum': '40b95cd2e8ccfa77724058832cc9809bb3aa0c5cf990d8c7b10cf854315ccce5',
        'size_bytes': 258029728,
        'generation': 1792086684183512,
        'condition': 'host_os == "mac" and host_cpu == "arm64"',
      },
      {
        'object_name': 'Win/rust-toolchain-8a9dd7abdf013ec10cfeaaa3685feba18ef1c90c-1-llvmorg-24-init-14453-ge063be79.tar.xz',
        'sha256sum': '8d501e922bc40c4e3bb255e8e31783c027054bff27b17970150c399c80eaf647',
        'size_bytes': 426164384,
        'generation': 1792086687600249,
        'condition': 'host_os == "win"',
      },
    ],
  },
  'third_party/llvm-libclang': {
    'dep_type': 'gcs',
    'bucket': 'chromium-browser-clang',
    'objects': [
      {
        'object_name': 'Linux_x64/rust-libclang-8a9dd7abdf013ec10cfeaaa3685feba18ef1c90c-1-llvmorg-24-init-14453-ge063be79.tar.xz',
        'sha256sum': '505dfa0b8c6c7abb332437c83e1ba169595e53aa8eef8f0aa1ea7adce4576835',
        'size_bytes': 23017532,
        'generation': 1792086677820729,
        'condition': 'host_os == "linux" and non_git_source',
      },
      {
        'object_name': 'Mac/rust-libclang-8a9dd7abdf013ec10cfeaaa3685feba18ef1c90c-1-llvmorg-24-init-14453-ge063be79.tar.xz',
        'sha256sum': 'add54dcb54194a627e6c0b7171aa06114064c231410e33f616a83948e4626882',
        'size_bytes': 23163236,
        'generation': 1792086682384306,
        'condition': 'host_os == "mac" and host_cpu == "x64"',
      },
      {
        'object_name': 'Mac_arm64/rust-libclang-8a9dd7abdf013ec10cfeaaa3685feba18ef1c90c-1-llvmorg-24-init-14453-ge063be79.tar.xz',
        'sha256sum': '3abad0aab3e8f49e2bb596a85cc88c38ee872bfe1dd55c6dc76fcfab9c6f0ba7',
        'size_bytes': 20838968,
        'generation': 1792086685890604,
        'condition': 'host_os == "mac" and host_cpu == "arm64"',
      },
      {
        'object_name': 'Win/rust-libclang-8a9dd7abdf013ec10cfeaaa3685feba18ef1c90c-1-llvmorg-24-init-14453-ge063be79.tar.xz',
        'sha256sum': 'b0716ed45f80b964b058414a80eb417272cb2e1df684c86efa31edf6ede31211',
        'size_bytes': 21797328,
        'generation': 1792086689442006,
        'condition': 'host_os == "win"',
      },
    ],
  },
  'buildtools/linux64': {
    'packages': [
      {
        'package': 'gn/gn/linux-${{arch}}',
        'version': Var('gn_version'),
      }
    ],
    'dep_type': 'cipd',
    'condition': 'host_os == "linux" and non_git_source',
  },
  'buildtools/mac': {
    'packages': [
      {
        'package': 'gn/gn/mac-${{arch}}',
        'version': Var('gn_version'),
      }
    ],
    'dep_type': 'cipd',
    'condition': 'host_os == "mac"',
  },
  'buildtools/win': {
    'packages': [
      {
        'package': 'gn/gn/windows-amd64',
        'version': Var('gn_version'),
      }
    ],
    'dep_type': 'cipd',
    'condition': 'host_os == "win"',
  },
  'third_party/compiler-rt/src': Var('chromium_git') +
    '/external/github.com/llvm/llvm-project/compiler-rt.git' + '@' +
    Var('compiler_rt_revision'),
  'third_party/libc++/src': Var('chromium_git') +
    '/external/github.com/llvm/llvm-project/libcxx.git' + '@' +
    Var('libcxx_revision'),
  'third_party/libc++abi/src': Var('chromium_git') +
    '/external/github.com/llvm/llvm-project/libcxxabi.git' + '@' +
    Var('libcxxabi_revision'),
  'third_party/libunwind/src': Var('chromium_git') +
    '/external/github.com/llvm/llvm-project/libunwind.git' + '@' +
    Var('libunwind_revision'),
  'third_party/llvm-libc/src': Var('chromium_git') +
    '/external/github.com/llvm/llvm-project/libc.git' + '@' +
    Var('llvm_libc_revision'),
  'third_party/google_benchmark/src': Var('chromium_git') + '/external/github.com/google/benchmark.git' + '@' + 'a6b4a9f00b36c19af9997d68a1cf6e0b5b3d032c',
  'third_party/boringssl/src': Var('boringssl_git') + '/boringssl.git' + '@' +  Var('boringssl_revision'),
  'third_party/catapult': Var('chromium_git') + '/catapult.git' + '@' + Var('catapult_revision'),
  'third_party/ced/src': Var('chromium_git') + '/external/github.com/google/compact_enc_det.git' + '@' + 'd127078cedef9c6642cbe592dacdd2292b50bb19',
  'third_party/depot_tools': Var('chromium_git') + '/chromium/tools/depot_tools.git' + '@' + 'b86fc981b72ab966f8260f73b4eca600b3b12677',
  'third_party/fontconfig/src': {
      'url': Var('chromium_git') + '/external/fontconfig.git' + '@' + 'd416ada7b20a1cdd5050b60a7a1bbdb3d9ddd2dc',
      'condition': 'checkout_linux',
  },
  'third_party/harfbuzz/src': Var('chromium_git') + '/external/github.com/harfbuzz/harfbuzz.git' + '@' + Var('harfbuzz_revision'),
  'third_party/googletest/src': Var('chromium_git') + '/external/github.com/google/googletest.git' + '@' + Var('googletest_revision'),
  'third_party/cpython3/host': {
      'packages': [
        {
          'package': 'infra/3pp/tools/cpython3/${{platform}}',
          'version': Var('cpython3_version'),
        },
      ],
      'condition': 'non_git_source',
      'dep_type': 'cipd',
  },
  'third_party/icu': Var('chromium_git') + '/chromium/deps/icu.git' + '@' + 'c670d124c9b6aa92c0b492cf543808300e0e6103',
  'third_party/libFuzzer/src': Var('chromium_git') + '/external/github.com/llvm/llvm-project/compiler-rt/lib/fuzzer.git' + '@' +  Var('libfuzzer_revision'),
  'third_party/fuzztest/src': Var('chromium_git') + '/external/github.com/google/fuzztest.git' + '@' + Var('fuzztest_revision'),
  'third_party/expat/src': Var('chromium_git') + '/external/github.com/libexpat/libexpat.git' + '@' + Var('libexpat_revision'),
  'third_party/lss': {
      'url': Var('chromium_git') + '/linux-syscall-support.git' + '@' + Var('lss_revision'),
      'condition': 'checkout_android or checkout_linux',
  },
  'third_party/nasm': {
      'url': Var('chromium_git') + '/chromium/deps/nasm.git' + '@' +
      '525a09a813be0f75b646ee93fc2a31c27b87d722'
  },
  'third_party/ninja': {
    'packages': [
      {
        'package': Var('ninja_package') + '${{platform}}',
        'version': Var('ninja_version'),
      }
    ],
    'condition': 'non_git_source',
    'dep_type': 'cipd',
  },
  'third_party/perfetto': Var('chromium_git') + '/external/github.com/google/perfetto.git' + '@' + '214c983f4c72c442d71415d9c81a7e1ed11566a7',
  'third_party/re2/src': Var('chromium_git') + '/external/github.com/google/re2.git' + '@' + '2da0056814cf180480a19f5cf811e7e1c054bf6d',
  'third_party/test_fonts/test_fonts': {
      'dep_type': 'gcs',
      'condition': 'non_git_source',
      'bucket': 'chromium-fonts',
      'objects': [
          {
              'object_name': '9c07d19d9c5ee1ff94f717e6fb17e0c8c354e6f9',
              'sha256sum': 'f0e9628f9e43e3f3476cde06a1849058de460e0e037b7449ce0d42b9a73c37d5',
              'size_bytes': 33413117,
              'generation': 1775663926405386
          },
      ],
  },
  'tools/resultdb': {
      'packages': [
        {
          'package': 'infra/tools/result_adapter/${{platform}}',
          'version': Var('result_adapter_revision'),
        },
      ],
      'condition': 'non_git_source',
      'dep_type': 'cipd',
  },
}

hooks = [
  {
    # Ensure that the DEPS'd "depot_tools" has its self-update capability
    # disabled.
    'name': 'disable_depot_tools_selfupdate',
    'pattern': '.',
    'action': [
        'python3',
        'third_party/depot_tools/update_depot_tools_toggle.py',
        '--disable',
    ],
  },
  {
    # Update the Windows toolchain if necessary.  Must run before 'clang' below.
    'name': 'win_toolchain',
    'pattern': '.',
    'condition': 'checkout_win',
    'action': ['python3', 'build/vs_toolchain.py', 'update', '--force'],
  },
  {
    # Update the Mac toolchain if necessary.
    'name': 'mac_toolchain',
    'pattern': '.',
    'condition': 'checkout_mac or checkout_ios',
    'action': ['python3', 'build/mac_toolchain.py'],
  },
  {
    # Use the Chromium commit, rather than this standalone project's history.
    'name': 'lastchange',
    'pattern': '.',
    'action': ['python3', 'scripts/update_lastchange.py',
               Var('chromium_revision')],
  },
  {
    'name': 'dsymutil_mac_arm64',
    'pattern': '.',
    'condition': 'host_os == "mac" and host_cpu == "arm64"',
    'action': [ 'python3',
                'third_party/depot_tools/download_from_google_storage.py',
                '--no_resume',
                '--bucket', 'chromium-browser-clang',
                '-s', 'tools/clang/dsymutil/bin/dsymutil.arm64.sha1',
                '-o', 'tools/clang/dsymutil/bin/dsymutil',
    ],
  },
  {
    'name': 'dsymutil_mac_x64',
    'pattern': '.',
    'condition': 'host_os == "mac" and host_cpu == "x64"',
    'action': [ 'python3',
                'third_party/depot_tools/download_from_google_storage.py',
                '--no_resume',
                '--bucket', 'chromium-browser-clang',
                '-s', 'tools/clang/dsymutil/bin/dsymutil.x64.sha1',
                '-o', 'tools/clang/dsymutil/bin/dsymutil',
    ],
  },
  {
    'name': 'rc_win',
    'pattern': '.',
    'condition': 'checkout_win and host_os == "win"',
    'action': [ 'python3',
                'third_party/depot_tools/download_from_google_storage.py',
                '--no_resume',
                '--bucket', 'chromium-browser-clang/rc',
                '-s', 'build/toolchain/win/rc/win/rc.exe.sha1',
    ],
  },
  {
    'name': 'rc_mac',
    'pattern': '.',
    'condition': 'checkout_win and host_os == "mac"',
    'action': [ 'python3',
                'third_party/depot_tools/download_from_google_storage.py',
                '--no_resume',
                '--bucket', 'chromium-browser-clang/rc',
                '-s', 'build/toolchain/win/rc/mac/rc.sha1',
    ],
  },
  {
    'name': 'rc_linux',
    'pattern': '.',
    'condition': 'checkout_win and host_os == "linux"',
    'action': [ 'python3',
                'third_party/depot_tools/download_from_google_storage.py',
                '--no_resume',
                '--bucket', 'chromium-browser-clang/rc',
                '-s', 'build/toolchain/win/rc/linux64/rc.sha1',
    ]
  },
]
