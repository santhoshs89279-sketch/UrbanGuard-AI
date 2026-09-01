package urbanguard_backend.dto;

public class DashboardSummary {

    private long totalVehicles;
    private long totalFires;
    private long totalAccidents;
    private long totalAlerts;

    public DashboardSummary(
            long totalVehicles,
            long totalFires,
            long totalAccidents,
            long totalAlerts) {

        this.totalVehicles = totalVehicles;
        this.totalFires = totalFires;
        this.totalAccidents = totalAccidents;
        this.totalAlerts = totalAlerts;
    }

    public long getTotalVehicles() {
        return totalVehicles;
    }

    public long getTotalFires() {
        return totalFires;
    }

    public long getTotalAccidents() {
        return totalAccidents;
    }

    public long getTotalAlerts() {
        return totalAlerts;
    }
}