package urbanguard_backend.service;

import urbanguard_backend.model.AccidentDetection;
import urbanguard_backend.model.Alert;
import urbanguard_backend.repository.AccidentDetectionRepository;
import urbanguard_backend.repository.AlertRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AccidentDetectionService {

    private final AccidentDetectionRepository accidentDetectionRepository;
    private final AlertRepository alertRepository;

    public AccidentDetectionService(
            AccidentDetectionRepository accidentDetectionRepository,
            AlertRepository alertRepository) {

        this.accidentDetectionRepository = accidentDetectionRepository;
        this.alertRepository = alertRepository;
    }

    // Save accident detection and automatically create an alert
    public AccidentDetection saveDetection(AccidentDetection detection) {

        // Save accident detection
        AccidentDetection savedDetection =
                accidentDetectionRepository.save(detection);

        // Create automatic alert
        Alert alert = new Alert(
                "ACCIDENT",
                "Accident detected with " +
                        (detection.getConfidence() * 100) + "% confidence",
                detection.getLocation(),
                detection.getSeverity()
        );

        alertRepository.save(alert);

        return savedDetection;
    }

    // Get all accident detections
    public List<AccidentDetection> getAllDetections() {
        return accidentDetectionRepository.findAll();
    }

    // Get accident detection by ID
    public AccidentDetection getDetectionById(Long id) {
        return accidentDetectionRepository.findById(id)
                .orElseThrow(() ->
                        new RuntimeException("Accident detection not found"));
    }

    // Delete accident detection
    public void deleteDetection(Long id) {
        accidentDetectionRepository.deleteById(id);
    }
}