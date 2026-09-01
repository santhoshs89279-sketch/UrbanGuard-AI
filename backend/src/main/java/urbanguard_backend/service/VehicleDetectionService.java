package urbanguard_backend.service;

import urbanguard_backend.model.Alert;
import urbanguard_backend.model.VehicleDetection;
import urbanguard_backend.repository.AlertRepository;
import urbanguard_backend.repository.VehicleDetectionRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class VehicleDetectionService {

    private final VehicleDetectionRepository vehicleDetectionRepository;
    private final AlertRepository alertRepository;

    public VehicleDetectionService(
            VehicleDetectionRepository vehicleDetectionRepository,
            AlertRepository alertRepository) {

        this.vehicleDetectionRepository = vehicleDetectionRepository;
        this.alertRepository = alertRepository;
    }

    // Save vehicle detection and check for restricted areas
    public VehicleDetection saveDetection(VehicleDetection detection) {

        // Save vehicle detection
        VehicleDetection savedDetection =
                vehicleDetectionRepository.save(detection);

        // Example restricted area condition
        if (detection.getLocation() != null &&
                detection.getLocation().toLowerCase().contains("restricted")) {

            Alert alert = new Alert(
                    "VEHICLE",
                    detection.getVehicleType() +
                            " detected in restricted area",
                    detection.getLocation(),
                    "HIGH"
            );

            alertRepository.save(alert);
        }

        return savedDetection;
    }

    // Get all vehicle detections
    public List<VehicleDetection> getAllDetections() {
        return vehicleDetectionRepository.findAll();
    }

    // Get vehicle detection by ID
    public VehicleDetection getDetectionById(Long id) {
        return vehicleDetectionRepository.findById(id)
                .orElseThrow(() ->
                        new RuntimeException("Vehicle detection not found"));
    }

    // Delete vehicle detection
    public void deleteDetection(Long id) {
        vehicleDetectionRepository.deleteById(id);
    }
}