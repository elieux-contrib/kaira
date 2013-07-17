#
#    Copyright (C) 2011-2013 Stanislav Bohm
#
#    This file is part of Kaira.
#
#    Kaira is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Kaira is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Kaira.  If not, see <http://www.gnu.org/licenses/>.
#


from writer import CppWriter, const_string, get_safe_name
import base.utils as utils

class Builder(CppWriter):

    def __init__(self, project, filename=None):
        CppWriter.__init__(self)
        self.filename = filename
        self.project = project

        # Real class used for thread representation,
        # CaThreadBase is cast to this type
        self.thread_class = "ca::Thread"

        # Generate packing function for all structures
        self.generate_all_pack = False


def write_first_lines(builder):
    builder.line("/* This file is automatically generated")
    builder.line("   do not edit this file directly! */")
    builder.emptyline()

def write_header(builder):
    write_first_lines(builder)
    builder.line("#include \"{0}.h\"", builder.project.get_name())

def write_header_file(builder):
    write_first_lines(builder)
    guard = "KAIRA_PROJECT_{0}".format(get_safe_name(builder.project.get_name()))
    builder.line("#ifndef {0}", guard)
    builder.line("#define {0}", guard)
    builder.line('#include <cailie.h>')
    builder.line('#include <algorithm>')
    builder.line('#include <stdlib.h>')
    builder.line('#include <stdio.h>')
    builder.line('#include <sstream>')
    builder.emptyline()
    write_parameters_forward(builder)
    builder.emptyline()
    if builder.project.get_head_code():
        builder.line_directive("*head", 1)
        builder.raw_text(builder.project.get_head_code())
        builder.emptyline()
    builder.line("#endif // {0}", guard)

def write_parameters_forward(builder):
    builder.line("struct param")
    builder.block_begin()
    for p in builder.project.get_parameters():
        if p.get_type() == "int":
            builder.line("static ca::ParameterInt {0};", p.get_name())
        elif p.get_type() == "double":
            builder.line("static ca::ParameterDouble {0};", p.get_name())
        elif p.get_type() == "std::string":
            builder.line("static ca::ParameterString {0};", p.get_name())
        else:
            raise utils.PtpException("Invalid type '{0}' for parameter '{1}'".format(
                                     p.get_type(), p.name))
    builder.write_class_end()

def write_parameters(builder):
    for p in builder.project.get_parameters():
        policy = "ca::PARAMETER_" + p.get_policy().upper()
        if p.get_policy() == "mandatory":
            default = ""
        else:
            default = ", " + p.default
        if p.get_type() == "int":
            builder.line("ca::ParameterInt param::{0}({1}, {2}, {3}{4});",
                         p.name,
                         const_string(p.name),
                         const_string(p.description),
                         policy,
                         default)
        elif p.get_type() == "double":
            builder.line("ca::ParameterDouble param::{0}({1}, {2}, {3}{4});",
                         p.name,
                         const_string(p.name),
                         const_string(p.description),
                         policy,
                         default)
        elif p.get_type() == "std::string":
            builder.line("ca::ParameterString param::{0}({1}, {2}, {3}{4});",
                         p.name,
                         const_string(p.name),
                         const_string(p.description),
                         policy,
                         default)
        else:
            utils.PtpException("Invalid type '{0}' for parameter '{1}'".format(
                                    p.get_type(), p.name))


def write_basic_definitions(builder):
    write_parameters(builder)
