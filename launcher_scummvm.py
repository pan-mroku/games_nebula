#!/usr/bin/env python2
# -*- Mode: Python; coding: utf-8; indent-tabs-install_mode: t; c-basic-offset: 4; tab-width: 4 -*-

import sys, os, subprocess, re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import ConfigParser
import gettext

global_config_file = os.getenv('HOME') + '/.games_nebula/config/config.ini'
global_config_parser = ConfigParser.ConfigParser()
global_config_parser.read(global_config_file)
gtk_theme = global_config_parser.get('visuals', 'gtk_theme')
gtk_dark = global_config_parser.getboolean('visuals', 'gtk_dark')
icon_theme = global_config_parser.get('visuals', 'icon_theme')
font = global_config_parser.get('visuals','font')
screen = Gdk.Screen.get_default()
gsettings = Gtk.Settings.get_for_screen(screen)
gsettings.set_property('gtk-theme-name', gtk_theme)
gsettings.set_property('gtk-application-prefer-dark-theme', gtk_dark)
gsettings.set_property('gtk-icon-theme-name', icon_theme)
gsettings.set_property('gtk-font-name', font)

global_scummvm =  global_config_parser.get('emulation settings', 'scummvm')
global_scummvm_path = global_config_parser.get('emulation settings', 'scummvm_path')
global_scummvm_version = global_config_parser.get('emulation settings', 'scummvm_version')
global_monitor = global_config_parser.getint('emulation settings', 'monitor')

goglib_install_dir = global_config_parser.get('goglib preferences', 'goglib_install_dir')
mylib_install_dir = global_config_parser.get('mylib preferences', 'mylib_install_dir')

nebula_dir = sys.path[0]
app_icon = GdkPixbuf.Pixbuf.new_from_file(nebula_dir + '/images/icon.png')

gettext.bindtextdomain('games_nebula', nebula_dir + '/locale')
gettext.textdomain('games_nebula')
_ = gettext.gettext

class GUI:

    def __init__(self, game_name, scummvm_game_name):

        self.game_name = game_name
        self.scummvm_game_name = scummvm_game_name

        if os.path.exists(goglib_install_dir + '/' + game_name):
            self.install_dir = goglib_install_dir
        elif os.path.exists(mylib_install_dir + '/' + game_name):
            self.install_dir = mylib_install_dir

        self.config_load()

        self.set_game_path()

        self.create_main_window()

    def set_game_path(self):

        config_file = self.install_dir + '/' + self.game_name + '/scummvmrc'
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)

        game_path = self.install_dir + '/' + self.game_name + '/game'
        config_parser.set(self.scummvm_game_name, 'path', game_path)
        config_parser.set(self.scummvm_game_name, 'savepath', game_path)

        new_config_file = open(config_file, 'w')
        config_parser.write(new_config_file)
        new_config_file.close()

    def config_load(self):

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)

        if not config_parser.has_section('Settings'):
            self.scummvm = 'global'
            self.scummvm_path = global_scummvm_path
            self.scummvm_version = global_scummvm_version
            self.monitor = global_monitor
            self.launcher = True
            self.show_banner = True

            config_parser.add_section('Settings')
            config_parser.set('Settings', 'scummvm', self.scummvm)
            config_parser.set('Settings', 'scummvm_path', self.scummvm_path)
            config_parser.set('Settings', 'scummvm_version', self.scummvm_version)
            config_parser.set('Settings', 'monitor', self.monitor)
            config_parser.set('Settings', 'launcher', self.launcher)
            config_parser.set('Settings', 'show_banner', self.show_banner)

            new_config_file = open(config_file, 'w')
            config_parser.write(new_config_file)
            new_config_file.close()

        else:
            self.scummvm = config_parser.get('Settings', 'scummvm')
            self.scummvm_path = config_parser.get('Settings', 'scummvm_path')
            self.scummvm_version = config_parser.get('Settings', 'scummvm_version')
            self.monitor = config_parser.getint('Settings', 'monitor')
            self.launcher = config_parser.getboolean('Settings', 'launcher')
            self.show_banner = config_parser.getboolean('Settings', 'show_banner')

    def config_save(self):

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)

        config_parser.set('Settings', 'scummvm', self.scummvm)
        config_parser.set('Settings', 'scummvm_path', self.scummvm_path)
        config_parser.set('Settings', 'scummvm_version', self.scummvm_version)
        config_parser.set('Settings', 'monitor', self.monitor)
        config_parser.set('Settings', 'launcher', self.launcher)
        config_parser.set('Settings', 'show_banner', self.show_banner)

        new_config_file = open(config_file, 'w')
        config_parser.write(new_config_file)
        new_config_file.close()

    def get_monitors(self):

        self.monitors_list = []
        proc = subprocess.Popen(['xrandr'],stdout=subprocess.PIPE)
        for line in proc.stdout.readlines():

            if re.compile(r'\b({0})\b'.format('connected'), flags=re.IGNORECASE).search(line):
                if 'primary' in line:
                    self.monitors_list.append(line.split(' ')[0] + ' ' + line.split(' ')[3].split('+')[0])
                else:
                    self.monitors_list.append(line.split(' ')[0] + ' ' + line.split(' ')[2].split('+')[0])
            if 'primary' in line:
                self.monitor_primary = line.split(' ')[0] + ' ' + line.split(' ')[3].split('+')[0]

    def get_banner(self):

        goglib_banners_dir = os.getenv('HOME') + '/.games_nebula/images/goglib_banners'
        mylib_banners_dir = os.getenv('HOME') + '/.games_nebula/images/mylib_banners'
        if os.path.exists(goglib_banners_dir + '/' + self.game_name + '.jpg'):
            self.banner_path = goglib_banners_dir + '/' + self.game_name + '.jpg'
        else:
            self.banner_path = mylib_banners_dir + '/' + self.game_name + '.jpg'

    def quit_app(self, window, event):
        self.config_save()
        Gtk.main_quit()

    def create_main_window(self):

        self.get_banner()
        self.get_monitors()

        self.main_window = Gtk.Window(
            title = _("Games Nebula"),
            type = Gtk.WindowType.TOPLEVEL,
            window_position = Gtk.WindowPosition.CENTER_ALWAYS,
            resizable = False,
            icon = app_icon,
            )
        self.main_window.connect('delete-event', self.quit_app)

        self.grid = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 10,
            column_spacing = 10,
            column_homogeneous = True,
            )

        self.banner = Gtk.Image(
            file = self.banner_path,
            no_show_all = True
            )

        self.banner.set_visible(self.show_banner)

        self.expander = Gtk.Expander(
            label = _("ScummVM")
            )

        self.frame = Gtk.Frame(
            #label = _("ScummVM"),
            label_xalign = 0.5,
            #margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.frame_grid = Gtk.Grid(
            column_homogeneous = True,
            #row_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.rbutton_global = Gtk.RadioButton(
            name = 'global',
            label = _("Global settings")
            )

        self.rbutton_sys = Gtk.RadioButton(
            name = 'system',
            label = _("System version")
            )
        self.rbutton_sys.join_group(self.rbutton_global)

        self.rbutton_path = Gtk.RadioButton(
            name = 'path',
            label = _("From directory"),
            )
        self.rbutton_path.join_group(self.rbutton_global)

        if self.scummvm == 'global':
            self.rbutton_global.set_active(True)
        elif self.scummvm == 'system':
            self.rbutton_sys.set_active(True)
        if self.scummvm == 'path':
            self.rbutton_path.set_label(_("From directory:"))
            self.rbutton_path.set_active(True)

        self.filechooser_button = Gtk.FileChooserButton(
            title = _("Select a directory"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            no_show_all = True
            )
        self.filechooser_button.set_filename(self.scummvm_path)

        self.combobox_version = Gtk.ComboBoxText(
            no_show_all = True
            )

        self.populate_scummvm_versions_combobox()

        self.filechooser_button.connect('file-set', self.cb_filechooser_button)
        self.combobox_version.connect('changed', self.cb_combobox_version)

        self.label_version = Gtk.Label(
            label = _("Version:"),
            halign = Gtk.Align.CENTER,
            )

        self.button_settings = Gtk.Button(
            label = _("Game specific ScummVM settings"),
            )
        self.button_settings.connect('clicked', self.cb_button_settings)

        self.frame_grid.attach(self.label_version, 0, 0, 2, 1)
        self.frame_grid.attach(self.rbutton_global, 0, 1, 2, 1)
        self.frame_grid.attach(self.rbutton_sys, 0, 2, 2, 1)
        self.frame_grid.attach(self.rbutton_path, 0, 3, 2, 1)
        self.frame_grid.attach(self.filechooser_button, 0, 4, 1, 1)
        self.frame_grid.attach(self.combobox_version, 1, 4, 1, 1)
        self.frame_grid.attach(self.button_settings, 0, 5, 2, 1)
        self.frame.add(self.frame_grid)
        self.expander.add(self.frame)

        self.rbutton_global.connect('toggled', self.cb_rbuttons)
        self.rbutton_sys.connect('toggled', self.cb_rbuttons)
        self.rbutton_path.connect('toggled', self.cb_rbuttons)

        if (self.scummvm == 'global') or (self.scummvm == 'system'):
            self.filechooser_button.set_visible(False)
            self.combobox_version.set_visible(False)
        else:
            self.filechooser_button.set_visible(True)
            self.combobox_version.set_visible(True)

        self.label_monitor = Gtk.Label(
            label = _("Monitor"),
            )
        self.combobox_monitor = Gtk.ComboBoxText()

        for output in self.monitors_list:
            self.combobox_monitor.append_text(output.translate(None, '\n'))
        self.combobox_monitor.set_active(self.monitor)

        self.combobox_monitor.connect('changed', self.cb_combobox_monitor)

        self.button_game = Gtk.Button(
            label = _("Launch game")
            )

        self.button_game.connect('clicked', self.cb_button_game)

        self.checkbutton_show_launcher = Gtk.CheckButton(
            label = _("Always show launcher")
            )

        if self.launcher == True:
            self.checkbutton_show_launcher.set_active(True)
        else:
            self.checkbutton_show_launcher.set_active(False)

        self.checkbutton_show_launcher.connect('clicked', self.cb_checkbutton_show_launcher)

        self.checkbutton_show_banner = Gtk.CheckButton(
            halign = Gtk.Align.END,
            valign = Gtk.Align.START,
            active = self.show_banner
            )

        self.checkbutton_show_banner.connect('toggled', self.cb_checkbutton_show_banner)

        self.grid.attach(self.checkbutton_show_banner, 0, 0, 2, 1)
        self.grid.attach(self.banner, 0, 0, 2, 1)
        self.grid.attach(self.expander, 0, 1, 2, 1)
        self.grid.attach(self.label_monitor, 0, 2, 1, 1)
        self.grid.attach(self.combobox_monitor, 1, 2, 1, 1)
        self.grid.attach(self.button_game, 0, 3, 2, 1)
        self.grid.attach(self.checkbutton_show_launcher, 0, 4, 2, 1)
        self.main_window.add(self.grid)

        if self.launcher == True:
            self.main_window.show_all()
        else:
            self.launch_game()

    def populate_scummvm_versions_combobox(self):

        ver_list = []

        path = self.filechooser_button.get_filename()
        full_list = os.listdir(path)

        for o in full_list:
            if os.path.isdir(path + '/' + o):
                ver_list.append(o)

        ver_list = sorted(ver_list)

        for i in range(len(ver_list)):
            self.combobox_version.append_text(ver_list[i])
            if ver_list[i] == self.scummvm_version:
                self.combobox_version.set_active(i)

    def cb_filechooser_button(self, button):
        self.scummvm_path = button.get_filename()
        self.combobox_version.get_model().clear()
        self.populate_scummvm_versions_combobox()

    def cb_combobox_version(self, combobox):
        self.scummvm_version = combobox.get_active_text()

    def cb_rbuttons(self, button):
        if button.get_name() == 'global':
            self.rbutton_path.set_label(_("From directory"))
            self.filechooser_button.set_visible(False)
            self.combobox_version.set_visible(False)
            self.scummvm = 'global'
        elif button.get_name() == 'system':
            self.rbutton_path.set_label(_("From directory"))
            self.filechooser_button.set_visible(False)
            self.combobox_version.set_visible(False)
            self.scummvm = 'system'
        else:
            self.rbutton_path.set_label(_("From directory:"))
            self.filechooser_button.set_visible(True)
            self.combobox_version.set_visible(True)
            self.scummvm = 'path'

    def cb_combobox_monitor(self, combobox):
        self.monitor = combobox.get_active()

    def cb_button_settings(self, button):

        output = self.combobox_monitor.get_active_text().split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        if self.scummvm == 'global':

            if global_scummvm == 'system':
                launch_command = 'scummvm --no-fullscreen -c ' + self.install_dir \
                + '/' + self.game_name + '/scummvmrc'
            if global_scummvm == 'path':
                launch_command = global_scummvm_path + '/' + global_scummvm_version + \
                '/bin/scummvm --no-fullscreen -c ' + self.install_dir \
                + '/' + self.game_name + '/scummvmrc'

        elif self.scummvm == 'system':
            launch_command = 'scummvm --no-fullscreen -c ' + self.install_dir \
            + '/' + self.game_name + '/scummvmrc'

        elif self.scummvm == 'path':
            launch_command = self.scummvm_path + '/' + self.scummvm_version + \
            '/bin/scummvm --no-fullscreen -c ' + self.install_dir \
            + '/' + self.game_name + '/scummvmrc'

        os.system(launch_command)

        output = self.monitor_primary.split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.main_window.show()

    def cb_button_game(self, button):
        self.launch_game()

    def launch_game(self):

        output = self.combobox_monitor.get_active_text().split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        if self.scummvm == 'global':
            if global_scummvm == 'system':
                scummvm_bin = 'scummvm'
            if global_scummvm == 'path':
                scummvm_bin = global_scummvm_path + '/' + global_scummvm_version + '/bin/scummvm'

        elif self.scummvm == 'system':
            scummvm_bin = 'scummvm'

        elif self.scummvm == 'path':
            scummvm_bin = self.scummvm_path + '/' + self.scummvm_version + '/bin/scummvm'

        launch_command = scummvm_bin + ' -c ' + self.install_dir + '/' +\
        self.game_name + '/scummvmrc ' + self.scummvm_game_name

        os.system(launch_command)

        output = self.monitor_primary.split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.config_save()

        sys.exit()

    def cb_checkbutton_show_launcher(self, button):
        if button.get_active() == False:
            self.launcher = False
        else:
            self.launcher = True

    def cb_checkbutton_show_banner(self, button):
        if button.get_active() == False:
            self.show_banner = False
            self.banner.set_visible(False)
        else:
            self.show_banner = True
            self.banner.set_visible(True)

def main():
    import sys
    app = GUI(sys.argv[1], sys.argv[2])
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
