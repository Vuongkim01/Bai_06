# Kim Duy Vương
# 20237410

from datetime import date
from typing import Optional
from enums import DeviceStatus


class BorrowingException(Exception):
    """
    Ngoại lệ cơ sở cho tất cả các lỗi nghiệp vụ liên quan đến mượn và trả thiết bị.
    """

    def __init__(self, message: str, inner_exception: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.inner_exception = inner_exception


class DeviceUnavailableException(BorrowingException):
    """
    Phát sinh khi thiết bị được yêu cầu mượn không ở trạng thái sẵn sàng (Available).
    """

    def __init__(self, device_id: str, current_status: DeviceStatus) -> None:
        self.device_id = device_id
        self.current_status = current_status
        super().__init__(
            f"Thiết bị '{device_id}' hiện không sẵn sàng (Trạng thái hiện tại: {current_status.value})."
        )


class BorrowLimitExceededException(BorrowingException):
    """
    Phát sinh khi người mượn đã đạt số lượng thiết bị tối đa cho phép trên một phiếu mượn.
    """

    def __init__(self, borrower_id: str, maximum_devices: int) -> None:
        self.borrower_id = borrower_id
        self.maximum_devices = maximum_devices
        super().__init__(
            f"Người mượn '{borrower_id}' đã đạt giới hạn tối đa ({maximum_devices} thiết bị/phiếu)."
        )


class InvalidBorrowPeriodException(BorrowingException):
    """
    Phát sinh khi số ngày mượn không dương (<= 0) hoặc vượt quá số ngày tối đa của thiết bị.
    """

    def __init__(self, device_id: str, requested_days: int, max_allowed_days: int) -> None:
        self.device_id = device_id
        self.requested_days = requested_days
        self.max_allowed_days = max_allowed_days
        super().__init__(
            f"Thời hạn mượn thiết bị '{device_id}' không hợp lệ "
            f"(Yêu cầu: {requested_days} ngày, Giới hạn tối đa: {max_allowed_days} ngày)."
        )


class DuplicateDeviceException(BorrowingException):
    """
    Phát sinh khi thêm cùng một thiết bị hai lần vào chung một phiếu mượn.
    """

    def __init__(self, device_id: str) -> None:
        self.device_id = device_id
        super().__init__(f"Thiết bị '{device_id}' đã tồn tại trong phiếu mượn này.")


class DeviceNotInSlipException(BorrowingException):
    """
    Phát sinh khi thực hiện trả một thiết bị không thuộc phiếu mượn hiện tại.
    """

    def __init__(self, device_id: str, slip_id: str) -> None:
        self.device_id = device_id
        self.slip_id = slip_id
        super().__init__(f"Thiết bị '{device_id}' không thuộc phiếu mượn '{slip_id}'.")


class DeviceAlreadyReturnedException(BorrowingException):
    """
    Phát sinh khi yêu cầu trả một thiết bị đã được hoàn trả trước đó.
    """

    def __init__(self, device_id: str, returned_date: Optional[date] = None) -> None:
        self.device_id = device_id
        self.returned_date = returned_date
        date_str = returned_date.strftime("%d/%m/%Y") if returned_date else "N/A"
        super().__init__(f"Thiết bị '{device_id}' đã được trả trước đó vào ngày {date_str}.")


class InvalidReturnDateException(BorrowingException):
    """
    Ngoại lệ bổ sung: Phát sinh khi ngày trả thực tế nhỏ hơn ngày mượn thiết bị.
    """

    def __init__(self, device_id: str, borrowed_date: date, returned_date: date) -> None:
        self.device_id = device_id
        self.borrowed_date = borrowed_date
        self.returned_date = returned_date
        super().__init__(
            f"Ngày trả thiết bị '{device_id}' ({returned_date.strftime('%d/%m/%Y')}) không hợp lệ "
            f"vì trước ngày mượn ({borrowed_date.strftime('%d/%m/%Y')})."
        )