package urbanguard_backend.controller;

import urbanguard_backend.model.VehicleDetection;
import urbanguard_backend.service.VehicleDetectionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/vehicles")
@CrossOrigin(origins = "*")
public class VehicleDetectionController {

    private final VehicleDetectionService vehicleDetectionService;

    public VehicleDetectionController(
            VehicleDetectionService vehicleDetectionService) {
        this.vehicleDetectionService = vehicleDetectionService;
    }

    // Save a vehicle detection
    @PostMapping
    public ResponseEntity<VehicleDetection> createDetection(
            @RequestBody VehicleDetection detection) {

        return ResponseEntity.ok(
                vehicleDetectionService.saveDetection(detection)
        );
    }

    // Get all vehicle detections
    @GetMapping
    public ResponseEntity<List<VehicleDetection>> getAllDetections() {

        return ResponseEntity.ok(
                vehicleDetectionService.getAllDetections()
        );
    }

    // Get vehicle detection by ID
    @GetMapping("/{id}")
    public ResponseEntity<VehicleDetection> getDetectionById(
            @PathVariable Long id) {

        return ResponseEntity.ok(
                vehicleDetectionService.getDetectionById(id)
        );
    }

    // Delete vehicle detection
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDetection(
            @PathVariable Long id) {

        vehicleDetectionService.deleteDetection(id);
        return ResponseEntity.noContent().build();
    }
}