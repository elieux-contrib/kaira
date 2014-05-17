#ifndef _NULLPTR_H_
#define _NULLPTR_H_

#if __cplusplus <= 199711L

#if defined(_MSC_VER)
  #define ALWAYS_INLINE __forceinline
#elif defined(__GNUC__)
  #define ALWAYS_INLINE inline __attribute__((always_inline))
#else
  #define ALWAYS_INLINE inline
#endif

/**
* Anonymous class, to be used instead of <code>0</code> or <code>NULL</code>.
* Enables the selection of the correct form when methods are overloaded for
* both pointers & integrals types.
*/
const class
{
  public:
#if defined(__GNUC__) && (__GNUC__ == 4) && (__GNUC_MINOR__ == 5) && (__GNUC_PATCHLEVEL < 2)
  ALWAYS_INLINE operator void*() const // works around bug #45383
  {
    return 0;
  }
#endif // #if defined(__GNUC__) && (__GNUC__ == 4) && __(__GNUC_MINOR__ == 5) && (__GNUC_PATCHLEVEL < 3)

  template<typename T>
  ALWAYS_INLINE operator T*() const
  {
    return 0;
  }

  template<class C, typename T>
  ALWAYS_INLINE operator T C::*() const
  {
    return 0;
  }

  private:
  void operator &() const; // not implemented on purpose

} nullptr = {}; //  The empty brace initializer fills the ISO C++
                //  (in 8.5 [dcl.ini] paragraph 9) requirements:
                //
                //  If no initializer is specified for an object, and the
                //  object is of (possibly cv-qualified) non-POD class
                //  type (or array thereof), the object shall be
                //  default-initialized; if the object is of
                //  const-qualified type, the underlying class type shall
                //  have a user-declared default constructor

#endif

#endif
