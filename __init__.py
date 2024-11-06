import os

def create_init_files():
    directories = ['tests', 'utils']
    for directory in directories:
        init_file = os.path.join(directory, '__init__.py')
        with open(init_file, 'w') as f:
            pass
        print(f"Created {init_file}")

if __name__ == "__main__":
    create_init_files()