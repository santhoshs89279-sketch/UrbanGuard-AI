package urbanguard_backend.service;

import urbanguard_backend.dto.DashboardSummary;
import urbanguard_backend.repository.AccidentDetectionRepository;
import urbanguard_backend.repository.AlertRepository;
import urbanguard_backend.repository.FireDetectionRepository;
import urbanguard_backend.repository.VehicleDetectionRepository;
import org.springframework.stereotype.Service;

@Service
public class DashboardService {

    private final VehicleDetectionRepository vehicleRepository;
    private final FireDetectionRepository fireRepository;
    private final AccidentDetectionRepository accidentRepository;
    private final AlertRepository alertRepository;

    public DashboardService(
            VehicleDetectionRepository vehicleRepository,
            FireDetectionRepository fireRepository,
            AccidentDetectionRepository accidentRepository,
            AlertRepository alertRepository) {

        this.vehicleRepository = vehicleRepository;
        this.fireRepository = fireRepository;
        this.accidentRepository = accidentRepository;
        this.alertRepository = alertRepository;
    }

    public DashboardSummary getDashboardSummary() {

        long totalVehicles = vehicleRepository.count();
        long totalFires = fireRepository.count();
        long totalAccidents = accidentRepository.count();
        long totalAlerts = alertRepository.count();

        return new DashboardSummary(
                totalVehicles,
                totalFires,
                totalAccidents,
                totalAlerts
        );
    }
}