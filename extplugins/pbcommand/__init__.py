# -*- coding: utf-8 -*-
#
# PBCommand For Urban Terror plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 PtitBigorneau - www.ptitbigorneau.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.4'


import b3
import b3.plugin
import b3.events
from b3.functions import getCmd

import time, threading, thread, re
from time import gmtime, strftime
import calendar

class PbcommandPlugin(b3.plugin.Plugin):

    _adminPlugin = None
    _test = None
    _listmap = []
    _gametype = {
        0:'FreeForAll',
        1:'LastManStanding',
        3:'TeamDeathMatch',
        4:'Team Survivor',
        5:'Follow the Leader',
        6:'Capture and Hold',
        7:'Capture The Flag',
        8:'Bombmode',
        9:'Jump',
        10:'Freeze Tag',
        11:'GunGame'
    }

    def onStartup(self):
        
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return False

        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = getCmd(self, cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)

    def cmd_putteam(self, data, client, cmd=None):
        
        """\
        <name> <team> - Put a player in red, blue or spectator
        """
        
        if data:
            
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
            
            client.message('!putteam <playername> <red, blue or spectator>')
            return
        
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        
        steam = input[1]
        
        if not sclient:
            
            return False
        
        if not steam:
            
            client.message('!putteam <playername> <red, blue or spectator>')
            return False
               
        if (steam == "red") or (steam == "blue") or (steam == "spec") or (steam == "spectator"):
            
            if steam == 'spec':
                steam = 'spectator'
        
        else:
            
            client.message('!putteam <playername> <red, blue or spectator>')
            return False
                    
        if sclient:
                
                self.verbose('Putteam client: %s to team: %s' % (sclient.cid, steam))
                self.console.write('forceteam %s %s' % (sclient.cid, steam))
        
        else:
            return False

    def cmd_currentmap(self, data, client, cmd=None):
        
        """\
        Current map
        """

        map = self.console.game.mapName

        if map[:4] == 'ut4_': map = map[4:]
        
        elif map[:3] == 'ut_': map = map[3:]

        client.message('^3Current Map is : ^5%s^7'%(map))
        
    def cmd_infoserver(self, data, client, cmd=None):
        
        """\
        info server
        """
        
        gametype = self.console.getCvar('g_gametype').getInt()
        
        gametype=self._gametype[gametype]
            
        cursor = self.console.storage.query("""
        SELECT *
        FROM clients
        ORDER BY time_edit
        """)
        
        tp = 0
        
        if cursor.EOF:

            cursor.close()            
            return False
        
        while not cursor.EOF:
        
            sr = cursor.getRow()
            
            cursor.moveNext()
            
            tp += 1
            
        cursor.close()
        
        map = self.console.game.mapName
                
        if map[:4] == 'ut4_': map = map[4:]
        
        elif map[:3] == 'ut_': map = map[3:]

        client.message('^3Name Server is : ^5%s^7'%(self.console.getCvar('sv_hostname').getString()))

        client.message('^3Adresse : ^5%s^7'%(self.console._publicIp +':'+ str(self.console._port)))
        client.message('^3GameType : ^5%s^3'%(gametype))
        client.message('^3TimeLimit : ^5%s minutes^7'%( self.console.getCvar('timelimit').getInt()))
        client.message('^3Map : ^5%s^7'%(map))
        client.message('^3Total Players : ^5%s^7'%(tp))
                
    def cmd_statserver(self, data, client, cmd=None):
        
        """\
        info stat server
        """
        
        cursor = self.console.storage.query("""
        SELECT *
        FROM clients
        ORDER BY time_edit
        """)
        
        tp = 0
        tpd = 0
        tph = 0
        
        time_epoch = time.time() 
        time_struct = time.gmtime(time_epoch)
        date = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
        mysql_time_struct = time.strptime(date, '%Y-%m-%d %H:%M:%S') 
        mdate = calendar.timegm( mysql_time_struct)
        
        if cursor.EOF:

            cursor.close()            
            return False
        
        while not cursor.EOF:
            sr = cursor.getRow()
            
            dbdate = sr['time_edit']
    
            if mdate - 86400 <= dbdate:
            
                tpd += 1
            
            if mdate - 3600 <= dbdate:
            
                tph += 1
            
            cursor.moveNext()
            tp += 1
            
        cursor.close()
    
        client.message('^3Total Players : ^5%s^7'%(tp))
        client.message('^3Total Players in the last 24 hours : ^5%s^7'%(tpd))
        client.message('^3Total Players in last hour : ^5%s^7'%(tph))

    def cmd_pbmapcycle(self, data, client, cmd=None):
        
        """\
        mapcycle
        """
        
        mapcycletxt = self.console.getCvar('g_mapcycle').getString()
        homepath = self.console.getCvar('fs_homepath').getString()
        gamepath = self.console.getCvar('fs_game').getString()
        mapcyclefile = homepath + "/" + gamepath + "/" + mapcycletxt

        fichier = open(mapcyclefile, "r")
        self.maps = ""
        self.client = client
        for map in fichier:
       
            map = map.replace(" ","")
            map = map.replace("\n","")
            map = map.replace("\r","")
            
            if map != "":
                
                if self._test == None:
            
                    if "{" in map:
                        self._test = "test"
                        continue
            
                    else:
                        self._listmap.append(map)
        
                if self._test != None:
            
                    if "}" in map:
                        self._test = None

        thread.start_new_thread(self.mapcycle, ())

        fichier.close()

    def mapcycle(self):

        maps = ""

        for map in self._listmap:

            if map != "":
            
                if map[:4] == 'ut4_': map = map[4:]
                elif map[:3] == 'ut_': map = map[3:]

                if maps != "":
                    maps = maps + ", " + "^5%s^7"%(map)

                else:
                    maps = "^5%s^7"%(map)

        self.client.message('%s'%(maps))

    def cmd_messageprivate(self, data, client, cmd=None):
        
        """\
        <client> <message> - private message
        """
        
        if data:
            
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
            
            client.message('!messageprivate <playername> <message>')
            return
        
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        
        message = input[1]
        
        if not sclient:
            
            return False
        
        if not message:
            
            client.message('!messageprivate <playername> <message>')
            return False
               
        if sclient:

            sclient.message('%s^3[pm]^7: %s'%(client.exactName, message))
        
        else:
            return False
