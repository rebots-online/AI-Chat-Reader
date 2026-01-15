# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
# Meson build configuration for AI Chat Reader GNOME application

project('ai-chat-reader',
  version: '1.0.0',
  meson_version: '>= 0.59.0',
  license: 'Proprietary',
)

# Dependencies
gjs_dep = dependency('gjs-1.0', version: '>= 1.72.0')
gtk4_dep = dependency('gtk4', version: '>= 4.6.0')
libadwaita_dep = dependency('libadwaita-1', version: '>= 1.2.0')

# Application ID and paths
app_id = 'org.gnome.AI-Chat-Reader'
prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
pkgdatadir = join_paths(datadir, meson.project_name())

# Compile GSettings schema
gnome = import('gnome')
gnome.compile_schemas(
  build_by_default: true,
  depend_files: files('data/org.gnome.AI-Chat-Reader.gschema.xml'),
)

# Install schema
install_data(
  'data/org.gnome.AI-Chat-Reader.gschema.xml',
  install_dir: join_paths(datadir, 'glib-2.0', 'schemas'),
)

# Install desktop file
install_data(
  'data/org.gnome.AI-Chat-Reader.desktop',
  install_dir: join_paths(datadir, 'applications'),
)

# Install icon
install_data(
  'data/org.gnome.AI-Chat-Reader.svg',
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
)

# Configure and install launcher script
conf = configuration_data()
conf.set('GJS', find_program('gjs').full_path())
conf.set('PKGDATADIR', pkgdatadir)
conf.set('VERSION', meson.project_version())

configure_file(
  input: 'bin/ai-chat-reader.in',
  output: 'ai-chat-reader',
  configuration: conf,
  install: true,
  install_dir: bindir,
  install_mode: 'rwxr-xr-x',
)

# Install JavaScript source files
install_subdir('src',
  install_dir: pkgdatadir,
  strip_directory: false,
)

# Install Python conversion scripts
install_subdir('scripts',
  install_dir: pkgdatadir,
  strip_directory: false,
)

# Post-install script for schema compilation
meson.add_install_script('scripts/post-install.sh')
