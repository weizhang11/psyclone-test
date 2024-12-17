module test_main

  use test_module 

  real, allocatable :: a(:), b(:), c(:), d(:,:)
  integer :: nx, ny, nz

  public initial_test
  contains
  
  subroutine initial_test()

    integer :: i, j, k
    nx = 256
    ny = 128
    nz = 64

    allocate(a(nx), b(nx), c(nx), d(nz, nx))
   
    call random_number(a)
    call random_number(b)
    c = 0.0
    d = 0.0

    do i = 1, nx
       print*, a(i), b(i)
    end do

  end subroutine initial_test

  subroutine test_main_routine()

    integer :: i, j, k

    do i = 1, nx
       if (a(i) .gt. 0.5) then
          call test_subroutine1(b(i), c(i))

          do k = 1, nz
             d(k,i) = k + c(i)
          end do
       else
          do k = 1, nz
             d(k,i) = a(i)
          end do
       end if
    end do

    ! If called subroutine in module of other file
    do i = 1, nx
       call test_subroutine2(b(i), c(i))
    end do


    do k = 1, nz
       print*, sum(d(k,:))
    end do

  end subroutine test_main_routine

  subroutine test_subroutine1(bb, cc)

    real, intent(in) :: bb
    real, intent(inout) :: cc

    cc = bb*2
 
  end subroutine test_subroutine1
end module test_main
