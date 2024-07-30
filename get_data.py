import os                               # Opertaing System 
import json                             # to work with JSON files 
import shutil                           # Allos us to do some copy and overwrite operations 
from subprocess import PIPE, run        # Allows us to run any terminal command like compile and run go code
import sys                              # Allows us to have access to command line arguments

DIR_PATTERN = 'game'
GO_EXTENSION = '.go'
GO_COMPILE_COMMAND = ['go', 'build']

def find_all_dirs_patterns(source):
  path_pattern = []
  for root, dirs, files in os.walk(source):
    for directory in dirs:
      if DIR_PATTERN in directory.lower():
        path = os.path.join(source, directory)
        path_pattern.append(path)
    break
  return path_pattern

def crate_dir(target_path):
  if not os.path.exists(target_path):
    os.mkdir(target_path)

def get_name_from_path(paths, to_strip):
  new_names = []
  for path in paths:
    _, dir_name = os.path.split(path)
    new_dir_name = dir_name.replace(to_strip, "")
    new_names.append(new_dir_name)
  return new_names

def copy_and_overwrite(source, dest):
  if os.path.exists(dest):
    shutil.rmtree(dest)
  shutil.copytree(source, dest)

def make_json_metadata_file(path, dirs_path):
  data = {
    'directoriesNames': dirs_path,
    'numberOfDirs': len(dirs_path)
  }
  with open(path, "w") as f:
    json.dump(data, f)

def compile_go_code(path):
  code_file_name = None
  for root, dirs, files in os.walk(path):
    for file in files:
      if file.endswith(GO_EXTENSION):
        code_file_name = file
        break
    break
  if code_file_name is None:
    print("No Go files found in the directory.")
    return
  print('='*20)
  print(code_file_name)
  command = GO_COMPILE_COMMAND + [code_file_name]
  run_command(command, path)

def run_command(command, path):
  cwd = os.getcwd()
  try:
    os.chdir(path)
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print("Compile result:", result.stdout)
    if result.stderr:
      print("Compile errors:", result.stderr)
  except FileNotFoundError as e:
    print(f"Error: {e}")
  finally:
    os.chdir(cwd)
  
def main(source, target):
  cwd = os.getcwd() # Current work directory
  source_path = os.path.join(cwd, source)
  target_path = os.path.join(cwd, target)

  dirs_paths = find_all_dirs_patterns(source_path)
  new_dirs_paths = get_name_from_path(dirs_paths, '_game')

  crate_dir(target_path)

  for src, dest in zip(dirs_paths, new_dirs_paths):
    dest_path = os.path.join(target_path, dest)
    copy_and_overwrite(src, dest_path)
    # compile_go_code(dest_path)

  json_path = os.path.join(target_path, 'metadata.json')
  make_json_metadata_file(json_path, new_dirs_paths)

  


# Fin all 'game' directories from data
if __name__ == '__main__': # Run 
  args = sys.argv # Save the arguments from the command line
  if len(args) != 3:
    raise Exception('You must pass a source and target directory only')
  source, target = args[1:] # Skip the first argument that is the pyhton file 
  main(source, target)
