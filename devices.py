# Kim Duy Vương
# 20237410

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from enums import DeviceStatus


class Device(ABC):
    """
    Lớp trừu tượng cơ sở biểu diễn một thiết bị trong trường đại học.
    Đảm bảo các ràng buộc toàn vẹn về mã thiết bị, giá mua và năm đưa vào sử dụng.
    """

    def __init__(
        self,
        device_id: str,
        device_name: str,
        year_of_use: int,
        purchase_price: Decimal,
        status: DeviceStatus = DeviceStatus.AVAILABLE
    ) -> None:
        # Mã thiết bị không được rỗng và chỉ được thiết lập một lần khi khởi tạo
        if not device_id or not device_id.strip():
            raise ValueError("Mã thiết bị không được để trống.")
        self._device_id: str = device_id.strip()

        # Thiết lập các thuộc tính qua setter để tái sử dụng kiểm tra hợp lệ
        self.device_name = device_name
        self.year_of_use = year_of_use
        self.purchase_price = purchase_price
        self._status: DeviceStatus = status

    @property
    def device_id(self) -> str:
        """Mã định danh thiết bị (Read-only, chỉ thiết lập khi khởi tạo)."""
        return self._device_id

    @property
    def device_name(self) -> str:
        """Tên thiết bị."""
        return self._device_name

    @device_name.setter
    def device_name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Tên thiết bị không được để trống.")
        self._device_name = value.strip()

    @property
    def year_of_use(self) -> int:
        """Năm đưa thiết bị vào sử dụng."""
        return self._year_of_use

    @year_of_use.setter
    def year_of_use(self, value: int) -> None:
        current_year = date.today().year
        if value > current_year or value < 1950:
            raise ValueError(f"Năm đưa vào sử dụng ({value}) không được lớn hơn năm hiện tại ({current_year}).")
        self._year_of_use = value

    @property
    def purchase_price(self) -> Decimal:
        """Giá mua thiết bị."""
        return self._purchase_price

    @purchase_price.setter
    def purchase_price(self, value: Decimal) -> None:
        if value <= Decimal("0"):
            raise ValueError("Giá mua thiết bị phải lớn hơn 0.")
        self._purchase_price = Decimal(value)

    @property
    def status(self) -> DeviceStatus:
        """Trạng thái hoạt động hiện tại của thiết bị."""
        return self._status

    @abstractmethod
    def calculate_annual_maintenance_cost(self) -> Decimal:
        """
        Phương thức trừu tượng tính chi phí bảo trì dự kiến trong một năm.
        Các lớp dẫn xuất bắt buộc phải ghi đè phương thức này.
        """
        pass

    def __str__(self) -> str:
        """Ghi đè phương thức biểu diễn thông tin thiết bị dưới dạng chuỗi."""
        return (
            f"[{self.device_id}] {self.device_name} | Năm SD: {self.year_of_use} | "
            f"Giá mua: {self.purchase_price:,.0f}đ | Trạng thái: {self.status.value} | "
            f"Phí bảo trì/năm: {self.calculate_annual_maintenance_cost():,.0f}đ"
        )


class TeachingDevice(Device, ABC):
    """
    Lớp trừu tượng biểu diễn thiết bị phục vụ giảng dạy có thể mượn - trả theo phiếu.
    Mở rộng từ lớp Device với giới hạn số ngày/tiết mượn tối đa và đơn giá phạt trả muộn.
    """

    def __init__(
        self,
        device_id: str,
        device_name: str,
        year_of_use: int,
        purchase_price: Decimal,
        max_borrow_days: int,
        max_borrow_periods: int,
        daily_late_fee: Decimal,
        status: DeviceStatus = DeviceStatus.AVAILABLE
    ) -> None:
        super().__init__(device_id, device_name, year_of_use, purchase_price, status)

        if max_borrow_days <= 0:
            raise ValueError("Số ngày mượn tối đa phải lớn hơn 0.")
        if max_borrow_periods <= 0:
            raise ValueError("Số tiết mượn tối đa phải lớn hơn 0.")
        if daily_late_fee < Decimal("0"):
            raise ValueError("Đơn giá phạt trả muộn không được âm.")

        self._max_borrow_days = max_borrow_days
        self._max_borrow_periods = max_borrow_periods
        self._daily_late_fee = Decimal(daily_late_fee)

    @property
    def max_borrow_days(self) -> int:
        """Số ngày tối đa được phép mượn thiết bị."""
        return self._max_borrow_days

    @property
    def max_borrow_periods(self) -> int:
        """Số tiết học tối đa được phép mượn thiết bị."""
        return self._max_borrow_periods

    @property
    def daily_late_fee(self) -> Decimal:
        """Phí phạt trả muộn trên mỗi ngày quá hạn."""
        return self._daily_late_fee

    def mark_as_borrowed(self) -> None:
        """Chuyển trạng thái thiết bị sang đang được mượn (Borrowed)."""
        self._status = DeviceStatus.BORROWED

    def mark_as_available(self) -> None:
        """Chuyển trạng thái thiết bị về sẵn sàng (Available)."""
        self._status = DeviceStatus.AVAILABLE

    def mark_as_under_maintenance(self) -> None:
        """Chuyển trạng thái thiết bị sang đang bảo trì (UnderMaintenance)."""
        self._status = DeviceStatus.UNDER_MAINTENANCE

    def __str__(self) -> str:
        return f"{super().__str__()} | Giới hạn: {self.max_borrow_days} ngày ({self.max_borrow_periods} tiết)"


class ProjectorRemote(TeachingDevice):
    """
    Lớp dẫn xuất biểu diễn thiết bị: Điều khiển máy chiếu.
    Mặc định cho phép mượn tối đa 2 ngày (6 tiết), phí phạt trả muộn 20.000đ/ngày.
    """

    def __init__(
        self,
        device_id: str,
        device_name: str,
        year_of_use: int,
        purchase_price: Decimal,
        max_borrow_days: int = 2,
        max_borrow_periods: int = 6,
        status: DeviceStatus = DeviceStatus.AVAILABLE
    ) -> None:
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            year_of_use=year_of_use,
            purchase_price=purchase_price,
            max_borrow_days=max_borrow_days,
            max_borrow_periods=max_borrow_periods,
            daily_late_fee=Decimal("20000"),
            status=status
        )

    def calculate_annual_maintenance_cost(self) -> Decimal:
        """Chi phí bảo trì hằng năm = 5% giá mua + 30.000đ phí thay pin định kỳ."""
        return self.purchase_price * Decimal("0.05") + Decimal("30000")


class AirConditionerRemote(TeachingDevice):
    """
    Lớp dẫn xuất biểu diễn thiết bị: Điều khiển điều hòa.
    Mặc định cho phép mượn tối đa 5 ngày (10 tiết), phí phạt trả muộn 15.000đ/ngày.
    """

    def __init__(
        self,
        device_id: str,
        device_name: str,
        year_of_use: int,
        purchase_price: Decimal,
        max_borrow_days: int = 5,
        max_borrow_periods: int = 10,
        status: DeviceStatus = DeviceStatus.AVAILABLE
    ) -> None:
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            year_of_use=year_of_use,
            purchase_price=purchase_price,
            max_borrow_days=max_borrow_days,
            max_borrow_periods=max_borrow_periods,
            daily_late_fee=Decimal("15000"),
            status=status
        )

    def calculate_annual_maintenance_cost(self) -> Decimal:
        """Chi phí bảo trì hằng năm = 4% giá mua + 25.000đ vệ sinh bo mạch & thay pin."""
        return self.purchase_price * Decimal("0.04") + Decimal("25000")


class WirelessMicrophone(TeachingDevice):
    """
    Lớp dẫn xuất biểu diễn thiết bị: Micro không dây.
    Mặc định cho phép mượn tối đa 1 ngày (4 tiết), phí phạt trả muộn 50.000đ/ngày.
    """

    def __init__(
        self,
        device_id: str,
        device_name: str,
        year_of_use: int,
        purchase_price: Decimal,
        max_borrow_days: int = 1,
        max_borrow_periods: int = 4,
        status: DeviceStatus = DeviceStatus.AVAILABLE
    ) -> None:
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            year_of_use=year_of_use,
            purchase_price=purchase_price,
            max_borrow_days=max_borrow_days,
            max_borrow_periods=max_borrow_periods,
            daily_late_fee=Decimal("50000"),
            status=status
        )

    def calculate_annual_maintenance_cost(self) -> Decimal:
        """Chi phí bảo trì hằng năm = 10% giá mua + 80.000đ bảo dưỡng đầu thu sóng & pin sạc."""
        return self.purchase_price * Decimal("0.10") + Decimal("80000")