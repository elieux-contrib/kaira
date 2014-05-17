#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([Kaira-Gnulib], [0.1], [kaira@freelists.org])
AC_CONFIG_MACRO_DIR([m4])
AM_INIT_AUTOMAKE
AM_CONDITIONAL(GL_GENERATE_ALLOCA_H, true)
AM_CONDITIONAL(GL_GENERATE_ERRNO_H, true)
AM_CONDITIONAL(GL_GENERATE_NETINET_IN_H, true)
AM_CONDITIONAL(GL_GENERATE_STDALIGN_H, true)
AM_CONDITIONAL(GL_GENERATE_STDDEF_H, true)

# Checks for programs.
AC_PROG_RANLIB
AC_PROG_CC
gl_EARLY
gl_INIT

# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.
AC_FUNC_ALLOCA

AC_CONFIG_FILES(Makefile lib/Makefile)
AC_CONFIG_HEADERS(lib/config.h)
AC_OUTPUT
