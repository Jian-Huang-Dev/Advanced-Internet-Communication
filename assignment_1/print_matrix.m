function print_matrix( M )

fprintf('\n');

[r,c] = size(M);

for row = 1:r
    fprintf('%3.1f ', M(row,:) );
    fprintf('\n');
end

fprintf('\n');