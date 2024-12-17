module test_main
  use test_module
  implicit none
  real, allocatable, dimension(:), public :: a
  real, allocatable, dimension(:), public :: b
  real, allocatable, dimension(:), public :: c
  real, allocatable, dimension(:,:), public :: d
  integer, public :: nx
  integer, public :: ny
  integer, public :: nz
  public

  contains
  subroutine initial_test()
    integer :: i
    integer :: j
    integer :: k

    nx = 256
    ny = 128
    nz = 64
    ALLOCATE(a(1:nx), b(1:nx), c(1:nx), d(1:nz,1:nx))
    call random_number(a)
    call random_number(b)
    c = 0.0
    d = 0.0
    do i = 1, nx, 1
      ! PSyclone CodeBlock (unsupported code) reason:
      !  - Unsupported statement: Print_Stmt
      PRINT *, a(i), b(i)
    enddo

  end subroutine initial_test
  subroutine test_main_routine()
    integer :: i
    integer :: j
    integer :: k

    !$acc parallel
    !$acc loop independent collapse(1)
    do i = 1, nx, 1
      if (a(i) > 0.5) then
        c(i) = b(i) * 2
        !$acc loop vector
        do k = 1, nz, 1
          d(k,i) = k + c(i)
        enddo
      else
        !$acc loop vector
        do k = 1, nz, 1
          d(k,i) = a(i)
        enddo
      end if
    enddo
    !$acc end parallel
    !$acc parallel
    !$acc loop independent collapse(1)
    do i = 1, nx, 1
      c(i) = b(i) * 3
    enddo
    !$acc end parallel
    do k = 1, nz, 1
      ! PSyclone CodeBlock (unsupported code) reason:
      !  - Unsupported statement: Print_Stmt
      PRINT *, SUM(d(k, :))
    enddo

  end subroutine test_main_routine
  subroutine test_subroutine1(bb, cc)
    real, intent(in) :: bb
    real, intent(inout) :: cc

    !$acc routine seq
    cc = bb * 2

  end subroutine test_subroutine1

end module test_main
