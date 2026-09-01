package urbanguard_backend.repository;

import urbanguard_backend.model.AccidentDetection;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AccidentDetectionRepository
        extends JpaRepository<AccidentDetection, Long> {

}