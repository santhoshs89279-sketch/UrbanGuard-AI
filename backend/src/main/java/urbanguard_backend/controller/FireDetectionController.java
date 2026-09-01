package urbanguard_backend.controller;

import urbanguard_backend.model.FireDetection;
import urbanguard_backend.service.FireDetectionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/fire")
@CrossOrigin(origins = "*")
public class FireDetectionController {

    private final FireDetectionService fireDetectionService;

    public FireDetectionController(FireDetectionService fireDetectionService) {
        this.fireDetectionService = fireDetectionService;
    }

    // Create a fire detection
    @PostMapping
    public ResponseEntity<FireDetection> createDetection(
            @RequestBody FireDetection detection) {

        return ResponseEntity.ok(
                fireDetectionService.saveDetection(detection)
        );
    }

    // Get all fire detections
    @GetMapping
    public ResponseEntity<List<FireDetection>> getAllDetections() {
        return ResponseEntity.ok(
                fireDetectionService.getAllDetections()
        );
    }

    // Get fire detection by ID
    @GetMapping("/{id}")
    public ResponseEntity<FireDetection> getDetectionById(
            @PathVariable Long id) {

        return ResponseEntity.ok(
                fireDetectionService.getDetectionById(id)
        );
    }

    // Delete a fire detection
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDetection(
            @PathVariable Long id) {

        fireDetectionService.deleteDetection(id);
        return ResponseEntity.noContent().build();
    }
}