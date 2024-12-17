module test_module

  public test_subroutine2

  contains

  subroutine test_subroutine2(b, c)

    real, intent(in):: b
    real, intent(inout) :: c

    c = b*3

  end subroutine test_subroutine2



end module  test_module
