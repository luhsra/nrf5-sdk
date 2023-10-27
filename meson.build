project('nrf5-sdk', 'c',
  version : '0.1',
  default_options : ['warning_level=3'])

# This is just a wrapper project to download and patch the nRF5 SDK for the usage with LLVM

py3_mod = import('python')
py3_inst = py3_mod.find_installation('python3')

nrf5_sdk_proj = subproject('nRF5_SDK_15.3.0_59ac345')
nrf5_sdk_dir = nrf5_sdk_proj.get_variable('nrf5_sdk_dir')

nrf5_llvm = subproject('nrf5-llvm')
nrf5_llvm_script = nrf5_llvm.get_variable('nrfsvc_script')
nrf5_llvm_patches = nrf5_llvm.get_variable('patches')

patch_program = find_program('patch')

patch_args = []
foreach patch : nrf5_llvm_patches
  patch_args += ['--patch', patch]
endforeach

patched_sdk = meson.current_build_dir() / 'nrf5_sdk_patched'
run_command(
  py3_inst, files('patch.py'),
  '--output-dir', patched_sdk,
  patch_args,
  '--convert-script', nrf5_llvm_script,
  '--sdk-path', nrf5_sdk_dir,
  '--patch-program', patch_program.full_path(),
  check: true
)
