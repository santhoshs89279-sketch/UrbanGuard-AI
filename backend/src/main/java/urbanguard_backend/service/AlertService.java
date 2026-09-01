package urbanguard_backend.service;

import urbanguard_backend.model.Alert;
import urbanguard_backend.repository.AlertRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class AlertService {

    private final AlertRepository alertRepository;

    public AlertService(AlertRepository alertRepository) {
        this.alertRepository = alertRepository;
    }

    // Create Alert
    public Alert createAlert(Alert alert) {
        return alertRepository.save(alert);
    }

    // Get All Alerts
    public List<Alert> getAllAlerts() {
        return alertRepository.findAll();
    }

    // Get Alert by ID
    public Optional<Alert> getAlertById(Long id) {
        return alertRepository.findById(id);
    }

    // Delete Alert
    public void deleteAlert(Long id) {
        alertRepository.deleteById(id);
    }
}