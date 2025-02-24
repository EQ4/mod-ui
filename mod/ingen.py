#!/usr/bin/env python
# Ingen Python Interface
# Copyright 2012 David Robillard <http://drobilla.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from tornado import iostream, ioloop
try:
    from ingenasync import Error, ingen_bundle_path, lv2_path, IngenAsync
    from lilvlib import NS
except ImportError:
    from mod.ingen_async import NS, Error, ingen_bundle_path, lv2_path, IngenAsync
import os
import rdflib
import socket
import sys

try:
    import StringIO.StringIO as StringIO
except ImportError:
    from io import StringIO as StringIO

class Host(IngenAsync):
    def initial_setup(self, callback=lambda r:r):
        def step1(ok):
            if ok: self.set("/graph", "<http://moddevices.com/ns/modpedal#addressings>",
                                      "<ingen:/addressings.json>", step2)
            else: callback(False)
        def step2(ok):
            if ok: self.set("/graph", "<http://moddevices.com/ns/modpedal#screenshot>",
                                      "<ingen:/screenshot.png>", step3)
            else: callback(False)
        def step3(ok):
            if ok: self.set("/graph", "<http://moddevices.com/ns/modpedal#thumbnail>",
                                      "<ingen:/thumbnail.png>", step4)
            else: callback(False)
        def step4(ok):
            if ok: self.get("/engine", step5)
            else: callback(False)
        def step5(ok):
            if ok: self.get("/graph", callback)
            else: callback(False)

        self.set("/graph", "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
                           "<http://moddevices.com/ns/modpedal#Pedalboard>", step1)

    def load(self, bundlepath, callback=lambda r:r):
        self.copy("file://%s" % bundlepath, "/graph", callback)

    def load_uri(self, uri, callback=lambda r:r):
        self.copy(uri, "/graph", callback)

    def save(self, bundlepath, callback=lambda r:r):
        self.copy("/graph", "file://%s" % bundlepath, callback)

    def set_pedalboard_name(self, name, callback=lambda r:r):
        self.set("/graph", "doap:name", '"%s"' % name.replace('"','\\"'), callback)

    def set_pedalboard_size(self, width, height, callback=lambda r:r):
        def nextStep(ok):
            if ok: self.set("/graph", "<http://moddevices.com/ns/modpedal#height>", height, callback)
            else: callback(False)
        self.set("/graph", "<http://moddevices.com/ns/modpedal#width>", width, nextStep)

    def set_position(self, instance, x, y, callback=lambda r:r):
        def nextStep(ok):
            if ok: self.set(instance, "<%s>" % NS.ingen.canvasY, float(y), callback)
            else: callback(False)
        self.set(instance, "<%s>" % NS.ingen.canvasX, float(x), nextStep)

    #def param_get(self, port, callback=lambda r:r):
        #callback(1)

    def param_set(self, port, value, callback=lambda r:r):
        self.set(port, "ingen:value", str(value), callback)

    def enable(self, instance, value, callback=lambda r:r):
        value = "true" if value else "false"
        self.set(instance, "ingen:enabled", value, callback)

    def preset_load(self, instance, uri, callback=lambda r:r):
        self.set(instance, "<%s>" % NS.presets.preset, "<%s>" % uri, callback)

    def add_plugin(self, instance, uri, enabled, x, y, callback=lambda r:r):
        self.put(instance, '''
        a ingen:Block ;
        <http://lv2plug.in/ns/lv2core#prototype> <%s> ;
        ingen:enabled %s ;
        ingen:canvasX %f ;
        ingen:canvasY %f ;
''' % (uri, "true" if enabled else "false", float(x), float(y)), callback)

    def remove_plugin(self, instance, callback=lambda r:r):
        self.delete(instance, callback)

    #def cpu_load(self, callback=lambda r:r):
        #callback({'ok': True, 'value': 50})

    #def monitor(self, addr, port, status, callback=lambda r:r):
        #callback(True)

    def connect(self, tail, head, callback=lambda r:r):
        return self._send('''
[]
        a patch:Put ;
        patch:subject <> ;
        patch:body [
                a ingen:Arc ;
                ingen:tail <%s> ;
                ingen:head <%s> ;
        ] .
''' % (tail, head), callback)

    def disconnect(self, tail, head, callback=lambda r:r):
        return self._send('''
[]
        a patch:Delete ;
        patch:body [
                a ingen:Arc ;
                ingen:tail <%s> ;
                ingen:head <%s> ;
        ] .
''' % (tail, head), callback)

    def midi_learn(self, path, callback=lambda r:r):
        return self.set(path, "<http://lv2plug.in/ns/ext/midi#binding>",
                              "<http://lv2plug.in/ns/ext/patch#wildcard>", callback)

    def add_external_port(self, name, mode, typ, callback=lambda r:r):
        # mode should be Input or Output
        if mode not in ("Input", "Output"):
            callback(False)
            return

        # type should be Audio, CV or MIDI
        if typ not in ("Audio", "CV", "MIDI"):
            callback(False)
            return

        from random import randint
        x = 5.0 if mode == "Input" else 2300.0
        y = randint(50,250)

        if typ == "MIDI":
            portyp = "<http://lv2plug.in/ns/ext/atom#AtomPort>"
            extra  = """
            <http://lv2plug.in/ns/ext/atom#bufferType> <http://lv2plug.in/ns/ext/atom#Sequence> ;
            <http://lv2plug.in/ns/ext/atom#supports> <http://lv2plug.in/ns/ext/midi#MidiEvent> ;
            """
        elif typ == "CV":
            portyp = "<http://lv2plug.in/ns/lv2core#CVPort>"
            extra  = ""
        else:
            portyp = "<http://lv2plug.in/ns/lv2core#AudioPort>"
            extra  = ""

        msg = """
        <http://drobilla.net/ns/ingen#canvasX> "%f"^^<http://www.w3.org/2001/XMLSchema#float> ;
        <http://drobilla.net/ns/ingen#canvasY> "%f"^^<http://www.w3.org/2001/XMLSchema#float> ;
        <http://lv2plug.in/ns/lv2core#name> "%s" ;
        a <http://lv2plug.in/ns/lv2core#%sPort> ;
        a %s ;
        %s
        """ % (x, y, name, mode, portyp, extra)

        print("========================================> add_external_port", name)
        self.put("/graph/%s" % name.replace(" ", "_").replace("-","_").lower(), msg, callback)

    def remove_external_port(self, name, callback=lambda r:r):
        print("========================================> remove_external_port", name)
        self.delete("/graph/%s" % name.replace(" ", "_").replace("-","_").lower(), callback)

    #def add_bundle(self, bundle, callback=lambda r: r):
        #return False # FIXME, this is not right..
        #return self._send('''
#[]
        #a patch:Put ;
        #patch:subject <%s> ;
        #patch:body [
                #a atom:Path
        #] .
#''' % bundle, callback)
