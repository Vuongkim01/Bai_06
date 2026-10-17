# Kim Duy Vương
# 20237410

from abc import ABC, abstractmethod


class IBorrower(ABC):
    """
    Interface quy định thông tin và hành vi của đối tượng mượn thiết bị.
    """

    @property
    @abstractmethod
    def borrower_id(self) -> str:
        """Mã định danh người mượn."""
        pass

    @property
    @abstractmethod
    def full_name(self) -> str:
        """Họ và tên đầy đủ của người mượn."""
        pass

    @abstractmethod
    def get_maximum_devices(self) -> int:
        """Trả về số lượng thiết bị tối đa được phép mượn trên một phiếu."""
        pass


class Lecturer(IBorrower):
    """
    Lớp biểu diễn Giảng viên.
    Quy tắc nghiệp vụ: Giảng viên được mượn tối đa 3 thiết bị trên một phiếu.
    """

    def __init__(self, borrower_id: str, full_name: str) -> None:
        if not borrower_id or not borrower_id.strip():
            raise ValueError("Mã giảng viên không được để trống.")
        if not full_name or not full_name.strip():
            raise ValueError("Họ tên giảng viên không được để trống.")

        self._borrower_id = borrower_id.strip()
        self._full_name = full_name.strip()

    @property
    def borrower_id(self) -> str:
        return self._borrower_id

    @property
    def full_name(self) -> str:
        return self._full_name

    def get_maximum_devices(self) -> int:
        return 3

    def __str__(self) -> str:
        return f"Giảng viên: {self.full_name} ({self.borrower_id}) - Hạn mức: tối đa {self.get_maximum_devices()} thiết bị"


class TeachingAssistant(IBorrower):
    """
    Lớp biểu diễn Trợ giảng.
    Quy tắc nghiệp vụ: Trợ giảng được mượn tối đa 2 thiết bị trên một phiếu.
    """

    def __init__(self, borrower_id: str, full_name: str) -> None:
        if not borrower_id or not borrower_id.strip():
            raise ValueError("Mã trợ giảng không được để trống.")
        if not full_name or not full_name.strip():
            raise ValueError("Họ tên trợ giảng không được để trống.")

        self._borrower_id = borrower_id.strip()
        self._full_name = full_name.strip()

    @property
    def borrower_id(self) -> str:
        return self._borrower_id

    @property
    def full_name(self) -> str:
        return self._full_name

    def get_maximum_devices(self) -> int:
        return 2

    def __str__(self) -> str:
        return f"Trợ giảng: {self.full_name} ({self.borrower_id}) - Hạn mức: tối đa {self.get_maximum_devices()} thiết bị"