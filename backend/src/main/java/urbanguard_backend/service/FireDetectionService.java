package urbanguard_backend.service;

import urbanguard_backend.model.Alert;
import urbanguard_backend.model.FireDetection;
import urbanguard_backend.repository.AlertRepository;
import urbanguard_backend.repository.FireDetectionRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class FireDetectionService {

    private final FireDetectionRepository fireDetectionRepository;
    private final AlertRepository alertRepository;

    public FireDetectionService(
            FireDetectionRepository fireDetectionRepository,
            AlertRepository alertRepository) {

        this.fireDetectionRepository = fireDetectionRepository;
        this.alertRepository = alertRepository;
    }

    // Save fire detection and automatically create an alert
    public FireDetection saveDetection(FireDetection detection) {

        // Save fire detection
        FireDetection savedDetection =
                fireDetectionRepository.save(detection);

        // Create automatic alert
        Alert alert = new Alert(
                "FIRE",
                "Fire detected with " +
                        (detection.getConfidence() * 100) + "% confidence",
                detection.getLocation(),
                "HIGH"
        );

        alertRepository.save(alert);

        return savedDetection;
    }

    // Get all fire detections
    public List<FireDetection> getAllDetections() {
        return fireDetectionRepository.findAll();
    }

    // Get fire detection by ID
    public FireDetection getDetectionById(Long id) {
        return fireDetectionRepository.findById(id)
                .orElseThrow(() ->
                        new RuntimeException("Fire detection not found"));
    }

    // Delete fire detection
    public void deleteDetection(Long id) {
        fireDetectionRepository.deleteById(id);
    }
}